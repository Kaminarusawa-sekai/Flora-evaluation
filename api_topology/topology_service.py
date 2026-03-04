"""Main service interface for API topology management."""

from typing import List, Dict, Any, Optional
from .graph_builder import GraphBuilder
from .path_finder import PathFinder


class TopologyService:
    """Service for building and querying API dependency graphs."""

    def __init__(self, neo4j_uri: str = "bolt://localhost:7687",
                 neo4j_user: str = "neo4j",
                 neo4j_password: str = "password",
                 llm_client=None):
        self.builder = GraphBuilder(neo4j_uri, neo4j_user, neo4j_password, llm_client)
        self.finder = PathFinder(neo4j_uri, neo4j_user, neo4j_password)

    def build_graph(self, capabilities: List[Dict[str, Any]],
                    dependencies: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        """
        Build API dependency graph from capabilities.

        Args:
            capabilities: List of API capabilities
            dependencies: Optional explicit dependencies [{'from': 'api1', 'to': 'api2'}]

        Returns:
            Build statistics
        """
        return self.builder.build(capabilities, dependencies)

    def find_paths(self, start_api: str, end_api: str, max_depth: int = 5,
                   required_fields: List[str] = None) -> List[Dict[str, Any]]:
        """
        Find scored paths between two APIs.

        Args:
            start_api: Starting API operation_id
            end_api: Target API operation_id
            max_depth: Maximum path length
            required_fields: Optional list of required field names

        Returns:
            List of path dicts with scores and edge info
        """
        return self.finder.find_paths(start_api, end_api, max_depth, required_fields)

    def get_dependencies(self, api: str) -> Dict[str, List[str]]:
        """Get upstream and downstream dependencies for an API."""
        return self.finder.get_dependencies(api)

    def close(self):
        """Close database connections."""
        self.builder.close()
        self.finder.close()
