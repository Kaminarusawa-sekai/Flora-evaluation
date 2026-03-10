"""SQLite-based state management for mock resources."""

import sqlite3
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
from contextlib import contextmanager


class StateManager:
    """Manage resource state in SQLite with session isolation and constraints."""

    def __init__(self, db_path: str = ":memory:", session_id: Optional[str] = None):
        self.db_path = db_path
        self.session_id = session_id or "default"
        self.foreign_keys: Dict[str, str] = {}  # resource_type -> parent_type
        self.status_constraints: Dict[str, Dict[str, List[str]]] = {}  # resource_type -> {action -> allowed_statuses}
        self.cascade_rules: Dict[str, List[str]] = {}  # parent_type -> [child_types]
        self._conn = None
        self._init_db()

    def _init_db(self):
        """Initialize database schema with session support."""
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self._conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS resources (
                session_id TEXT NOT NULL,
                resource_type TEXT NOT NULL,
                resource_id TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                PRIMARY KEY (session_id, resource_type, resource_id)
            )
        """)

        self._conn.commit()

    def _get_connection(self):
        """Get the persistent connection."""
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return self._conn

    def set_foreign_key(self, resource_type: str, parent_type: str, parent_field: str = "id"):
        """Define foreign key constraint."""
        self.foreign_keys[resource_type] = {"parent_type": parent_type, "field": parent_field}

        # Auto-register cascade relationship
        if parent_type not in self.cascade_rules:
            self.cascade_rules[parent_type] = []
        if resource_type not in self.cascade_rules[parent_type]:
            self.cascade_rules[parent_type].append(resource_type)

    def set_status_constraint(self, resource_type: str, action: str, allowed_statuses: List[str]):
        """Define status-based constraint (e.g., can't delete PAID orders)."""
        if resource_type not in self.status_constraints:
            self.status_constraints[resource_type] = {}
        self.status_constraints[resource_type][action] = allowed_statuses

    def create_resource(self, resource_type: str, resource_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new resource with foreign key validation."""
        # Check foreign key constraint
        if resource_type in self.foreign_keys:
            fk_config = self.foreign_keys[resource_type]
            parent_type = fk_config["parent_type"]
            parent_field = fk_config["field"]
            parent_id = state.get(f"{parent_type}_{parent_field}")

            if parent_id and not self.get_state(parent_type, parent_id):
                raise ValueError(f"Foreign key violation: {parent_type} with id {parent_id} does not exist")

        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()
        cursor.execute(
            """
            INSERT OR REPLACE INTO resources (session_id, resource_type, resource_id, state, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (self.session_id, resource_type, resource_id, json.dumps(state), now, now)
        )

        conn.commit()
        return {"id": resource_id, **state}

    def get_state(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """Get resource state for current session."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT state FROM resources
            WHERE session_id = ? AND resource_type = ? AND resource_id = ?
            """,
            (self.session_id, resource_type, resource_id)
        )

        row = cursor.fetchone()

        if row:
            return json.loads(row[0])
        return None

    def list_resources(self, resource_type: str) -> List[Dict[str, Any]]:
        """List all resources of a type in current session."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT resource_id, state FROM resources
            WHERE session_id = ? AND resource_type = ?
            """,
            (self.session_id, resource_type)
        )

        rows = cursor.fetchall()

        return [{"id": row[0], **json.loads(row[1])} for row in rows]

    def update_resource(self, resource_type: str, resource_id: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Update resource state."""
        conn = self._get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()
        cursor.execute(
            """
            UPDATE resources
            SET state = ?, updated_at = ?
            WHERE session_id = ? AND resource_type = ? AND resource_id = ?
            """,
            (json.dumps(state), now, self.session_id, resource_type, resource_id)
        )

        conn.commit()
        return {"id": resource_id, **state}

    def delete_resource(self, resource_type: str, resource_id: str, cascade: bool = True):
        """Delete a resource with status constraint check and optional cascade."""
        # Check status constraint
        if resource_type in self.status_constraints and "delete" in self.status_constraints[resource_type]:
            current_state = self.get_state(resource_type, resource_id)
            if current_state:
                status = current_state.get("status")
                allowed = self.status_constraints[resource_type]["delete"]
                if status and status not in allowed:
                    raise ValueError(f"Cannot delete {resource_type} in status '{status}'")

        # Cascade delete children
        if cascade and resource_type in self.cascade_rules:
            for child_type in self.cascade_rules[resource_type]:
                children = self._find_children(child_type, resource_type, resource_id)
                for child_id in children:
                    self.delete_resource(child_type, child_id, cascade=True)

        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            DELETE FROM resources
            WHERE session_id = ? AND resource_type = ? AND resource_id = ?
            """,
            (self.session_id, resource_type, resource_id)
        )

        conn.commit()

    def _find_children(self, child_type: str, parent_type: str, parent_id: str) -> List[str]:
        """Find all children of a parent resource."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT resource_id, state FROM resources
            WHERE session_id = ? AND resource_type = ?
            """,
            (self.session_id, child_type)
        )

        children = []
        parent_field = f"{parent_type}_id"
        for row in cursor.fetchall():
            state = json.loads(row[1])
            if state.get(parent_field) == parent_id:
                children.append(row[0])

        return children

    def reset(self):
        """Reset state for current session only."""
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM resources WHERE session_id = ?", (self.session_id,))

        conn.commit()

    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None

    def __del__(self):
        """Cleanup on deletion."""
        self.close()

    @contextmanager
    def session(self, session_id: str):
        """Context manager for session isolation."""
        old_session = self.session_id
        self.session_id = session_id
        try:
            yield self
        finally:
            self.session_id = old_session
