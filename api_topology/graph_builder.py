"""Build API dependency graph in Neo4j."""

from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from .field_matcher import FieldMatcher, FieldMatch
from .path_extractor import PathExtractor
from .transformation_detector import TransformationDetector


class GraphBuilder:
    """Build and store API dependency graphs in Neo4j."""

    def __init__(self, uri: str, user: str, password: str, llm_client=None):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.matcher = FieldMatcher(llm_client=llm_client)
        self.path_extractor = PathExtractor()

    def build(self, capabilities: List[Dict[str, Any]],
              dependencies: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """Build graph from capabilities and dependencies."""
        with self.driver.session() as session:
            # Clear existing graph
            session.run("MATCH (n:API) DETACH DELETE n")

            # Create API nodes with fields
            api_count = 0
            api_map = {}  # operation_id -> api_data

            for cap in capabilities:
                for api in cap.get('apis', []):
                    # Flatten nested schemas if present
                    response_fields = api.get('response_fields', [])
                    if api.get('response_schema'):
                        response_fields = self.path_extractor.flatten_schema(api['response_schema'])

                    request_fields = api.get('request_fields', [])
                    if api.get('request_schema'):
                        request_fields = self.path_extractor.flatten_schema(api['request_schema'])

                    session.run(
                        """
                        CREATE (a:API {
                            operation_id: $operation_id,
                            method: $method,
                            path: $path,
                            summary: $summary,
                            capability: $capability,
                            response_fields: $response_fields,
                            request_fields: $request_fields
                        })
                        """,
                        operation_id=api['operation_id'],
                        method=api['method'],
                        path=api['path'],
                        summary=api.get('summary', ''),
                        capability=cap.get('name', ''),
                        response_fields=str(response_fields),
                        request_fields=str(request_fields)
                    )
                    api_map[api['operation_id']] = {
                        **api,
                        'capability': cap.get('name', ''),
                        'response_fields': response_fields,
                        'request_fields': request_fields
                    }
                    api_count += 1

            # Create explicit dependencies
            dep_count = 0
            if dependencies:
                for dep in dependencies:
                    session.run(
                        """
                        MATCH (a:API {operation_id: $from})
                        MATCH (b:API {operation_id: $to})
                        CREATE (a)-[:DEPENDS_ON {score: 1.0, type: 'CERTAIN'}]->(b)
                        """,
                        **dep
                    )
                    dep_count += 1

            # Infer dependencies from field matching
            inferred = self._infer_field_dependencies(session, api_map)

            return {
                'apis_created': api_count,
                'explicit_dependencies': dep_count,
                'inferred_dependencies': inferred
            }

    def _infer_field_dependencies(self, session, api_map: Dict[str, Dict]) -> int:
        """Infer dependencies based on field matching."""
        count = 0

        # Compare all API pairs
        api_list = list(api_map.values())
        for i, source_api in enumerate(api_list):
            response_fields = source_api.get('response_fields', [])
            if not response_fields:
                continue

            for target_api in api_list[i+1:]:
                request_fields = target_api.get('request_fields', [])
                if not request_fields:
                    continue

                # Check if same cluster
                same_cluster = source_api.get('capability') == target_api.get('capability')

                # Match fields
                best_score = 0.0
                matched_fields = []

                for resp_field in response_fields:
                    for req_field in request_fields:
                        score = self.matcher.calculate_score(
                            resp_field, req_field, same_cluster,
                            source_api.get('summary', ''),
                            target_api.get('summary', '')
                        )
                        match_type = self.matcher.classify_match(score)

                        if match_type:
                            best_score = max(best_score, score)

                            # Detect transformation requirement
                            transform = TransformationDetector.detect_transformation(
                                resp_field, req_field
                            )

                            matched_fields.append({
                                'source': resp_field.get('path', resp_field['name']),
                                'target': req_field.get('path', req_field['name']),
                                'score': score,
                                'requires_transformation': transform is not None,
                                'transformation_type': transform
                            })

                # Create edge if match found
                if best_score >= self.matcher.final_threshold:
                    match_type = self.matcher.classify_match(best_score)
                    session.run(
                        """
                        MATCH (a:API {operation_id: $from})
                        MATCH (b:API {operation_id: $to})
                        MERGE (a)-[r:DEPENDS_ON]->(b)
                        SET r.score = $score, r.type = $type, r.matched_fields = $fields
                        """,
                        **{'from': source_api['operation_id']},
                        to=target_api['operation_id'],
                        score=best_score,
                        type=match_type,
                        fields=str(matched_fields)
                    )
                    count += 1

        return count

    def close(self):
        """Close database connection."""
        self.driver.close()
