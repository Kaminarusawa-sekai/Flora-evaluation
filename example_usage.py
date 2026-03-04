"""
Example usage of the four service modules.

This demonstrates how to use the API normalization, topology, scenario generation,
and stateful mock services together.
"""

from api_normalization import NormalizationService
from api_topology import TopologyService
from scenario_generation import ScenarioGenerationService
from stateful_mock import MockService


def main():
    """Example workflow using all four services."""

    # 1. Normalize Swagger API
    print("=== Step 1: API Normalization ===")
    norm_service = NormalizationService()
    capabilities = norm_service.normalize_swagger("example_swagger.json")
    print(f"Extracted {capabilities['total_capabilities']} capabilities from {capabilities['total_apis']} APIs")

    # 2. Build API topology graph
    print("\n=== Step 2: Build API Topology ===")
    topo_service = TopologyService(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password"
    )

    build_result = topo_service.build_graph(capabilities['capabilities'])
    print(f"Created {build_result['apis_created']} API nodes")
    print(f"Inferred {build_result['inferred_dependencies']} dependencies")

    # 3. Find API paths
    print("\n=== Step 3: Find API Paths ===")
    paths = topo_service.find_paths("createUser", "deleteUser", max_depth=5)
    print(f"Found {len(paths)} paths from createUser to deleteUser")

    if paths:
        print(f"Example path: {' -> '.join(paths[0])}")

    # 4. Generate test scenarios
    print("\n=== Step 4: Generate Test Scenarios ===")
    scenario_service = ScenarioGenerationService()

    if paths:
        scenarios = scenario_service.generate_scenarios(paths[0], count=3)
        for i, result in enumerate(scenarios, 1):
            scenario = result['scenario']
            validation = result['validation']
            print(f"\nScenario {i}: {scenario['title']}")
            print(f"  Valid: {validation['is_valid']}, Score: {validation['score']:.2f}")

    # 5. Start mock server
    print("\n=== Step 5: Start Mock Server ===")
    mock_service = MockService(db_path="test_mock.db")

    server_info = mock_service.start_server(
        capabilities=capabilities['capabilities'],
        host="127.0.0.1",
        port=8000
    )
    print(f"Mock server running at {server_info['url']}")
    print(f"Registered {server_info['apis_registered']} APIs")

    # Keep server running
    print("\nPress Ctrl+C to stop the server...")
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping server...")
        mock_service.stop_server()
        topo_service.close()
        print("Done!")


if __name__ == "__main__":
    main()
