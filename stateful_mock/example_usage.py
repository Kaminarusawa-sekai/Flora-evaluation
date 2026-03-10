"""Example usage of enhanced stateful mock service."""
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from stateful_mock import MockService, ChaosRule

# Initialize service with memory database and chaos seed for reproducibility
service = MockService(db_path=":memory:", chaos_seed=42)

# Configure business constraints
service.configure_constraints(
    foreign_keys={
        "order": {"parent_type": "user", "field": "id"}
    },
    status_constraints={
        "order": {
            "delete": ["PENDING", "CANCELLED"]  # Can't delete PAID orders
        }
    }
)

# Add chaos rules
service.add_chaos_rule("fail_first_delete", ChaosRule(
    api_pattern="/orders/*",
    method="DELETE",
    trigger_count=1,  # First call fails
    action="fail_500"
))

service.add_chaos_rule("random_timeout", ChaosRule(
    api_pattern="*",
    probability=0.05,  # 5% chance
    action="fail_500"
))

service.add_chaos_rule("token_expiry", ChaosRule(
    api_pattern="/orders/*",
    trigger_count=3,
    action="token_expired"
))

# Define capabilities with schemas
capabilities = [
    {
        "name": "user",
        "apis": [
            {
                "operation_id": "create_user",
                "method": "POST",
                "path": "/users",
                "request_schema": {
                    "required": ["name", "email"],
                    "properties": {
                        "name": {"type": "string"},
                        "email": {"type": "string"},
                        "age": {"type": "integer"}
                    }
                }
            },
            {
                "operation_id": "get_user",
                "method": "GET",
                "path": "/users/{id}"
            }
        ]
    },
    {
        "name": "order",
        "apis": [
            {
                "operation_id": "create_order",
                "method": "POST",
                "path": "/orders",
                "request_schema": {
                    "required": ["user_id", "amount"],
                    "properties": {
                        "user_id": {"type": "string"},
                        "amount": {"type": "integer"}
                    }
                }
            },
            {
                "operation_id": "delete_order",
                "method": "DELETE",
                "path": "/orders/{id}"
            }
        ]
    }
]

# Start server
info = service.start_server(capabilities, port=8000)
print(f"Server started: {info}")

# Seed initial data
service.seed_data({
    "user": [
        {"id": "user1", "name": "Alice", "email": "alice@example.com"}
    ]
})

# Use session isolation for parallel tests
with service.session("test_001"):
    # This session has isolated state
    pass

with service.session("test_002"):
    # This session has different isolated state
    pass

# Export logs for analysis
logs = service.export_logs()
print(f"Total requests: {len(logs)}")

