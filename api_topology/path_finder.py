"""Find paths in API dependency graph."""

from typing import List, Dict, Any
from neo4j import GraphDatabase


class PathFinder:
    """Query API dependency graph for paths and relationships."""

    def __init__(self, uri: str, user: str, password: str, path_penalty: float = 1.2):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.path_penalty = path_penalty

    def find_paths(self, start_api: str, end_api: str, max_depth: int = 5,
                   required_fields: List[str] = None) -> List[Dict[str, Any]]:
        """Find scored paths between two APIs."""
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = (start:API {operation_id: $start})-[rels:DEPENDS_ON*1..%d]->(end:API {operation_id: $end})
                WHERE ALL(n IN nodes(path) WHERE size([m IN nodes(path) WHERE m = n]) = 1)
                WITH path, rels,
                     reduce(s = 0.0, r IN rels | s + coalesce(r.score, 0.5)) as total_score,
                     length(path) as path_length
                RETURN [node in nodes(path) | node.operation_id] as path,
                       total_score / (path_length ^ $penalty) as score,
                       [r IN rels | {type: r.type, score: r.score}] as edge_info
                ORDER BY score DESC
                LIMIT 100
                """ % max_depth,
                start=start_api,
                end=end_api,
                penalty=self.path_penalty
            )

            paths = []
            for record in result:
                path_data = {
                    'path': record['path'],
                    'score': record['score'],
                    'edge_info': record['edge_info']
                }

                # Filter by required fields if specified
                if required_fields:
                    if self._path_provides_fields(session, record['path'], required_fields):
                        paths.append(path_data)
                else:
                    paths.append(path_data)

            return paths

    def _path_provides_fields(self, session, path: List[str], required_fields: List[str]) -> bool:
        """Check if path provides all required fields."""
        # Get all response fields from APIs in path
        result = session.run(
            """
            MATCH (a:API)
            WHERE a.operation_id IN $path
            RETURN a.response_fields as fields
            """,
            path=path
        )

        available_fields = set()
        for record in result:
            fields_str = record['fields']
            # Parse field names from stored string representation
            if fields_str:
                import ast
                try:
                    fields = ast.literal_eval(fields_str)
                    for field in fields:
                        if isinstance(field, dict):
                            available_fields.add(field.get('name', ''))
                except:
                    pass

        return all(field in available_fields for field in required_fields)

    def get_dependencies(self, api: str) -> Dict[str, List[str]]:
        """Get upstream and downstream dependencies."""
        with self.driver.session() as session:
            # Downstream (APIs this one depends on)
            downstream = session.run(
                """
                MATCH (a:API {operation_id: $api})-[:DEPENDS_ON]->(b:API)
                RETURN b.operation_id as operation_id
                """,
                api=api
            )
            downstream_list = [record['operation_id'] for record in downstream]

            # Upstream (APIs that depend on this one)
            upstream = session.run(
                """
                MATCH (a:API)-[:DEPENDS_ON]->(b:API {operation_id: $api})
                RETURN a.operation_id as operation_id
                """,
                api=api
            )
            upstream_list = [record['operation_id'] for record in upstream]

            return {
                'depends_on': downstream_list,
                'depended_by': upstream_list
            }

    def close(self):
        """Close database connection."""
        self.driver.close()
