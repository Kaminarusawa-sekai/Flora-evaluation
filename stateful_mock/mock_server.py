"""FastAPI-based mock server with dynamic route registration."""

from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import re
from .state_manager import StateManager
from .chaos_engine import ChaosEngine

try:
    from jsonschema import validate, ValidationError as JsonSchemaError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


class MockServer:
    """Dynamic mock API server with chaos injection and validation."""

    def __init__(self, state_manager: StateManager, chaos_engine: Optional[ChaosEngine] = None):
        self.app = FastAPI(title="Stateful Mock API")
        self.state_manager = state_manager
        self.chaos_engine = chaos_engine or ChaosEngine()
        self.routes: Dict[str, Dict[str, Any]] = {}
        self.request_log: list = []
        self.call_counts: Dict[str, int] = {}  # For stale data tracking

        @self.app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
        async def handle_request(request: Request, path: str):
            return await self._handle_request(request, path)

    def register_api(self, operation_id: str, method: str, path: str, capability: str,
                     request_schema: Optional[Dict[str, Any]] = None):
        """Register an API endpoint with optional schema."""
        pattern = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', path)
        pattern = f"^{pattern}$"

        self.routes[f"{method}:{path}"] = {
            'operation_id': operation_id,
            'method': method,
            'path': path,
            'pattern': pattern,
            'capability': capability,
            'request_schema': request_schema
        }

    async def _handle_request(self, request: Request, path: str) -> Response:
        """Handle incoming request with chaos injection and validation."""
        method = request.method
        full_path = f"/{path}"

        # Log request
        self.request_log.append({"method": method, "path": full_path, "timestamp": None})

        # Chaos injection (highest priority)
        chaos_response = self.chaos_engine.should_inject(full_path, method)
        if chaos_response:
            return chaos_response

        # Find matching route
        route_info = self._match_route(method, full_path)
        if not route_info:
            return JSONResponse(status_code=404, content={"error": "Route not found"})

        # Extract path parameters and session
        match = re.match(route_info['pattern'], full_path)
        path_params = match.groupdict() if match else {}
        session_id = request.headers.get("X-Session-ID", self.state_manager.session_id)

        # Get request body
        try:
            body = await request.json() if method in ["POST", "PUT", "PATCH"] else {}
        except:
            body = {}

        # Schema validation
        if route_info.get('request_schema') and body:
            try:
                self._validate_schema(body, route_info['request_schema'])
            except ValueError as e:
                raise HTTPException(status_code=422, detail={"error": "Validation failed", "message": str(e)})

        # Handle with session context
        with self.state_manager.session(session_id):
            if method == "POST":
                return await self._handle_post(route_info, body, path_params)
            elif method == "GET":
                return await self._handle_get(route_info, path_params)
            elif method == "PUT":
                return await self._handle_put(route_info, body, path_params)
            elif method == "DELETE":
                return await self._handle_delete(route_info, path_params)
            else:
                return JSONResponse(content={"message": "OK"})

    def _validate_schema(self, data: Dict[str, Any], schema: Dict[str, Any]):
        """Advanced schema validation with jsonschema if available."""
        if HAS_JSONSCHEMA:
            try:
                validate(instance=data, schema=schema)
            except JsonSchemaError as e:
                raise ValueError(f"Schema validation failed: {e.message}")
        else:
            # Fallback to basic validation
            required = schema.get("required", [])
            properties = schema.get("properties", )

            for field in required:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")

            for field, value in data.items():
                if field in properties:
                    expected_type = properties[field].get("type")
                    if expected_type == "integer" and not isinstance(value, int):
                        raise ValueError(f"Field '{field}' must be integer")
                    elif expected_type == "string" and not isinstance(value, str):
                        raise ValueError(f"Field '{field}' must be string")

    def _match_route(self, method: str, path: str) -> Optional[Dict[str, Any]]:
        """Match request to registered route."""
        for key, route in self.routes.items():
            if route['method'] == method:
                if re.match(route['pattern'], path):
                    return route
        return None

    async def _handle_post(self, route_info: Dict, body: Dict, path_params: Dict) -> Response:
        """Handle POST request - create resource."""
        resource_type = route_info['capability']
        resource_id = body.get('id', path_params.get('id', f"auto_{len(self.request_log)}"))

        try:
            result = self.state_manager.create_resource(resource_type, resource_id, body)
            return JSONResponse(status_code=201, content=result)
        except ValueError as e:
            return JSONResponse(status_code=400, content={"error": str(e)})

    async def _handle_get(self, route_info: Dict, path_params: Dict) -> Response:
        """Handle GET request - read resource with stale data simulation."""
        resource_type = route_info['capability']
        resource_id = path_params.get('id')

        if resource_id:
            cache_key = f"{resource_type}:{resource_id}"

            # Check if should return stale data
            stale_data = self.chaos_engine.get_stale_data(cache_key)
            if stale_data and self.call_counts.get(cache_key, 0) == 1:
                # First call returns stale, cache fresh for next
                fresh_state = self.state_manager.get_state(resource_type, resource_id)
                if fresh_state:
                    self.chaos_engine.cache_stale_data(cache_key, None)  # Clear after use
                return JSONResponse(content=stale_data)

            state = self.state_manager.get_state(resource_type, resource_id)
            if state:
                # Cache for potential stale simulation
                self.chaos_engine.cache_stale_data(cache_key, state)
                self.call_counts[cache_key] = self.call_counts.get(cache_key, 0) + 1
                return JSONResponse(content=state)
            return JSONResponse(status_code=404, content={"error": "Not found"})
        else:
            items = self.state_manager.list_resources(resource_type)
            return JSONResponse(content={"items": items, "total": len(items)})

    def export_request_log(self) -> List[Dict[str, Any]]:
        """Export request log for analysis."""
        return self.request_log.copy()

    async def _handle_put(self, route_info: Dict, body: Dict, path_params: Dict) -> Response:
        """Handle PUT request - update resource."""
        resource_type = route_info['capability']
        resource_id = path_params.get('id')

        if not resource_id:
            return JSONResponse(status_code=400, content={"error": "ID required"})

        if not self.state_manager.get_state(resource_type, resource_id):
            return JSONResponse(status_code=404, content={"error": "Resource not found"})

        result = self.state_manager.update_resource(resource_type, resource_id, body)
        return JSONResponse(content=result)

    async def _handle_delete(self, route_info: Dict, path_params: Dict) -> Response:
        """Handle DELETE request - delete resource."""
        resource_type = route_info['capability']
        resource_id = path_params.get('id')

        if not resource_id:
            return JSONResponse(status_code=400, content={"error": "ID required"})

        try:
            self.state_manager.delete_resource(resource_type, resource_id)
            return JSONResponse(content={"id": resource_id, "status": "deleted"})
        except ValueError as e:
            return JSONResponse(status_code=400, content={"error": str(e)})
