"""Incremental graph update support."""

import hashlib
import json
from typing import Dict, Any, List, Set


class IncrementalBuilder:
    """Support incremental graph updates."""

    def __init__(self):
        self.api_hashes: Dict[str, str] = {}

    def compute_hash(self, api: Dict[str, Any]) -> str:
        """Compute hash for API definition."""
        key_fields = {
            'operation_id': api.get('operation_id'),
            'method': api.get('method'),
            'path': api.get('path'),
            'request_fields': api.get('request_fields', []),
            'response_fields': api.get('response_fields', [])
        }
        content = json.dumps(key_fields, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()

    def detect_changes(self, capabilities: List[Dict[str, Any]]) -> Dict[str, Set[str]]:
        """Detect added, modified, and removed APIs."""
        current_apis = {}
        for cap in capabilities:
            for api in cap.get('apis', []):
                op_id = api['operation_id']
                current_apis[op_id] = self.compute_hash(api)

        added = set(current_apis.keys()) - set(self.api_hashes.keys())
        removed = set(self.api_hashes.keys()) - set(current_apis.keys())
        modified = {
            op_id for op_id in current_apis
            if op_id in self.api_hashes and current_apis[op_id] != self.api_hashes[op_id]
        }

        self.api_hashes = current_apis

        return {
            'added': added,
            'modified': modified,
            'removed': removed
        }
