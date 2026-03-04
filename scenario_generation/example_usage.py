"""Example usage of enhanced scenario generation."""

from scenario_generation_service import ScenarioGenerationService

# Example API path and details
api_path = ["login", "list_orders", "get_order_detail", "cancel_order"]

api_details = {
    "login": {
        "method": "POST",
        "path": "/api/auth/login",
        "summary": "用户登录",
        "parameters": ["username", "password"],
        "responses": {"user_id": "string", "token": "string"}
    },
    "list_orders": {
        "method": "GET",
        "path": "/api/orders",
        "summary": "查询订单列表",
        "parameters": ["user_id", "token"],
        "responses": {"orders": [{"id": "string", "status": "string"}]}
    },
    "get_order_detail": {
        "method": "GET",
        "path": "/api/orders/{order_id}",
        "summary": "获取订单详情",
        "parameters": ["order_id", "token"],
        "responses": {"order": {"id": "string", "status": "string", "amount": "number"}}
    },
    "cancel_order": {
        "method": "POST",
        "path": "/api/orders/{order_id}/cancel",
        "summary": "取消订单",
        "parameters": ["order_id", "reason", "token"],
        "responses": {"success": "boolean"}
    }
}

# Parameter flow from topology analysis
parameter_flow = {
    "list_orders": {
        "user_id": "login.response.user_id",
        "token": "login.response.token"
    },
    "get_order_detail": {
        "order_id": "list_orders.response.orders[0].id",
        "token": "login.response.token"
    },
    "cancel_order": {
        "order_id": "get_order_detail.response.order.id",
        "token": "login.response.token"
    }
}

# Initialize service
service = ScenarioGenerationService()

# Generate scenarios
scenarios = service.generate_scenarios(
    api_path=api_path,
    api_details=api_details,
    parameter_flow=parameter_flow,
    scenario_types=['normal', 'exception'],
    count_per_type=1
)

# Print results
for i, result in enumerate(scenarios, 1):
    print(f"\n=== Scenario {i} ===")
    print(f"Type: {result['scenario']['scenario_type']}")
    print(f"Title: {result['scenario']['title']}")
    print(f"Valid: {result['validation']['is_valid']}")
    print(f"Score: {result['validation']['score']:.2f}")
    if result['validation']['warnings']:
        print(f"Warnings: {result['validation']['warnings']}")
