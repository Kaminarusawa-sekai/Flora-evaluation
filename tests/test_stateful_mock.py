"""
Unit tests for stateful_mock module.
"""

import pytest
import os
from stateful_mock.state_manager import StateManager
from stateful_mock.mock_server import MockServer


class TestStateManager:
    """Test StateManager functionality."""

    def test_create_and_get_resource(self, tmp_path):
        """Test resource creation and retrieval."""
        db_path = tmp_path / "test.db"
        manager = StateManager(str(db_path))

        # Create resource
        manager.create_resource('user', 'user1', {'name': 'John', 'email': 'john@example.com'})

        # Get resource
        state = manager.get_state('user', 'user1')

        assert state is not None
        assert state['name'] == 'John'
        assert state['email'] == 'john@example.com'

    def test_update_resource(self, tmp_path):
        """Test resource update."""
        db_path = tmp_path / "test.db"
        manager = StateManager(str(db_path))

        # Create and update
        manager.create_resource('user', 'user1', {'name': 'John'})
        manager.update_resource('user', 'user1', {'name': 'Jane'})

        # Verify update
        state = manager.get_state('user', 'user1')
        assert state['name'] == 'Jane'

    def test_delete_resource(self, tmp_path):
        """Test resource deletion."""
        db_path = tmp_path / "test.db"
        manager = StateManager(str(db_path))

        # Create and delete
        manager.create_resource('user', 'user1', {'name': 'John'})
        manager.delete_resource('user', 'user1')

        # Verify deletion
        state = manager.get_state('user', 'user1')
        assert state is None

    def test_reset(self, tmp_path):
        """Test state reset."""
        db_path = tmp_path / "test.db"
        manager = StateManager(str(db_path))

        # Create multiple resources
        manager.create_resource('user', 'user1', {'name': 'John'})
        manager.create_resource('user', 'user2', {'name': 'Jane'})

        # Reset
        manager.reset()

        # Verify all deleted
        assert manager.get_state('user', 'user1') is None
        assert manager.get_state('user', 'user2') is None


class TestMockServer:
    """Test MockServer functionality."""

    def test_register_api(self, tmp_path):
        """Test API registration."""
        db_path = tmp_path / "test.db"
        manager = StateManager(str(db_path))
        server = MockServer(manager)

        server.register_api('getUser', 'GET', '/users/{id}', 'users')

        assert 'GET:/users/{id}' in server.routes

    def test_match_route(self, tmp_path):
        """Test route matching."""
        db_path = tmp_path / "test.db"
        manager = StateManager(str(db_path))
        server = MockServer(manager)

        server.register_api('getUser', 'GET', '/users/{id}', 'users')

        route = server._match_route('GET', '/users/123')
        assert route is not None
        assert route['operation_id'] == 'getUser'
