"""Main service interface for stateful mock server."""

from typing import List, Dict, Any, Optional
import threading
import uvicorn
from contextlib import contextmanager
from .mock_server import MockServer
from .state_manager import StateManager
from .chaos_engine import ChaosEngine, ChaosRule


class MockService:
    """Service for managing stateful mock API server with chaos injection."""

    def __init__(self, db_path: str = ":memory:", chaos_seed: Optional[int] = None):
        self.state_manager = StateManager(db_path)
        self.chaos_engine = ChaosEngine(seed=chaos_seed)
        self.mock_server = MockServer(self.state_manager, self.chaos_engine)
        self.server_thread: Optional[threading.Thread] = None
        self.server = None

    def start_server(self, capabilities: List[Dict[str, Any]],
                     host: str = "127.0.0.1",
                     port: int = 8000) -> Dict[str, Any]:
        """Start mock server with given capabilities."""
        for cap in capabilities:
            for api in cap.get('apis', []):
                self.mock_server.register_api(
                    operation_id=api['operation_id'],
                    method=api['method'],
                    path=api['path'],
                    capability=cap.get('name', ''),
                    request_schema=api.get('request_schema')
                )

        config = uvicorn.Config(self.mock_server.app, host=host, port=port, log_level="error")
        self.server = uvicorn.Server(config)

        def run_server():
            self.server.run()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        return {
            'status': 'running',
            'url': f"http://{host}:{port}",
            'apis_registered': sum(len(cap.get('apis', [])) for cap in capabilities)
        }

    def add_chaos_rule(self, rule_id: str, rule: ChaosRule):
        """Add chaos injection rule."""
        self.chaos_engine.add_rule(rule_id, rule)

    def configure_constraints(self, foreign_keys: Dict[str, Dict] = None,
                            status_constraints: Dict[str, Dict] = None):
        """Configure business constraints."""
        if foreign_keys:
            for resource_type, config in foreign_keys.items():
                self.state_manager.set_foreign_key(resource_type, config['parent_type'], config.get('field', 'id'))

        if status_constraints:
            for resource_type, constraints in status_constraints.items():
                for action, allowed_statuses in constraints.items():
                    self.state_manager.set_status_constraint(resource_type, action, allowed_statuses)

    @contextmanager
    def session(self, session_id: str):
        """Context manager for isolated test session."""
        with self.state_manager.session(session_id):
            yield self

    def export_logs(self) -> List[Dict[str, Any]]:
        """Export request logs for analysis."""
        return self.mock_server.export_request_log()

    def seed_data(self, data: Dict[str, List[Dict[str, Any]]]):
        """Seed initial data from test scenario."""
        for resource_type, items in data.items():
            for item in items:
                resource_id = item.get('id', f"seed_{len(items)}")
                self.state_manager.create_resource(resource_type, resource_id, item)

    def stop_server(self):
        """Stop the mock server."""
        if self.server:
            self.server.should_exit = True
            if self.server_thread:
                self.server_thread.join(timeout=5)

    def get_state(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of a resource."""
        return self.state_manager.get_state(resource_type, resource_id)

    def reset_state(self):
        """Reset all state."""
        self.state_manager.reset()
