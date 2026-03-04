"""Example usage of API Topology Service with all features."""

from api_topology import TopologyService

# Sample API data with nested schemas
capabilities = [
    {
        "name": "User Management",
        "apis": [
            {
                "operation_id": "createUser",
                "method": "POST",
                "path": "/users",
                "summary": "Create a new user",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "user": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string", "description": "User unique identifier"},
                                "username": {"type": "string"}
                            }
                        }
                    }
                },
                "request_fields": [
                    {"name": "username", "type": "string", "location": "body"},
                    {"name": "email", "type": "string", "location": "body"}
                ]
            },
            {
                "operation_id": "getUser",
                "method": "GET",
                "path": "/users/{id}",
                "summary": "Get user by ID",
                "response_fields": [
                    {"name": "user_id", "type": "string", "location": "body"},
                    {"name": "username", "type": "string", "location": "body"}
                ],
                "request_fields": [
                    {"name": "id", "type": "string", "location": "path"}
                ]
            }
        ]
    },
    {
        "name": "Order Management",
        "apis": [
            {
                "operation_id": "createOrder",
                "method": "POST",
                "path": "/orders",
                "summary": "Create an order",
                "response_fields": [
                    {"name": "order_id", "type": "string", "location": "body"}
                ],
                "request_fields": [
                    {"name": "uid", "type": "string", "location": "body", "description": "User identifier"},
                    {"name": "product_id", "type": "string", "location": "body"}
                ]
            }
        ]
    }
]

if __name__ == "__main__":
    # Initialize service (optionally with LLM client)
    service = TopologyService(
        neo4j_uri="bolt://localhost:7687",
        neo4j_user="neo4j",
        neo4j_password="password",
        llm_client=None  # Pass your LLM client here if available
    )

    print("Building graph with advanced matching...")
    result = service.build_graph(capabilities)
    print(f"✓ Created {result['apis_created']} APIs")
    print(f"✓ Inferred {result['inferred_dependencies']} dependencies")

    print("\nFinding paths (with entity matching & semantic similarity)...")
    paths = service.find_paths("createUser", "createOrder")

    for i, path in enumerate(paths, 1):
        print(f"\nPath {i} (score: {path['score']:.3f}):")
        print(f"  Route: {' -> '.join(path['path'])}")
        for edge in path['edge_info']:
            print(f"    Edge type: {edge['type']}, score: {edge['score']:.2f}")

    service.close()
    print("\n✓ All features enabled: Entity canonicalization, Semantic matching, Nested schemas, Transformation detection")

