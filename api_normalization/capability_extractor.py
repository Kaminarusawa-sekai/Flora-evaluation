"""Extract capability models from clustered APIs with schema merging."""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict, Counter
import re


class CapabilityExtractor:
    """Extract high-level capabilities from API clusters with unified schema."""

    def extract(self, apis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract capabilities from clustered APIs."""
        clusters = defaultdict(list)
        atomic_capabilities = []

        for api in apis:
            cluster_id = api.get('cluster', -1)
            cluster_type = api.get('cluster_type', 'semantic')

            if cluster_type == 'atomic':
                # Atomic capability - single API
                atomic_cap = self._create_atomic_capability(api)
                atomic_capabilities.append(atomic_cap)
            else:
                clusters[cluster_id].append(api)

        capabilities = []
        for cluster_id, cluster_apis in clusters.items():
            if cluster_id == -1:  # Noise cluster - treat as atomic
                for api in cluster_apis:
                    atomic_cap = self._create_atomic_capability(api)
                    atomic_capabilities.append(atomic_cap)
                continue

            capability = self._create_capability(cluster_id, cluster_apis)
            capabilities.append(capability)

        # Combine all capabilities
        all_capabilities = capabilities + atomic_capabilities

        return {
            'capabilities': all_capabilities,
            'total_apis': len(apis),
            'total_capabilities': len(all_capabilities),
            'semantic_capabilities': len(capabilities),
            'atomic_capabilities': len(atomic_capabilities)
        }

    def _create_atomic_capability(self, api: Dict[str, Any]) -> Dict[str, Any]:
        """Create an atomic capability from a single API."""
        operation_id = api.get('operation_id', 'unknown')
        action_verb = api.get('action_verb', '')

        name = api.get('summary') or api.get('tags', ['Unknown'])[0] if api.get('tags') else operation_id

        return {
            'id': f"atomic_{operation_id}",
            'name': name,
            'type': 'atomic',
            'description': api.get('description', ''),
            'action_verb': action_verb,
            'apis': [{
                'operation_id': operation_id,
                'method': api['method'],
                'path': api['path'],
                'normalized_path': api.get('normalized_path', api['path']),
                'summary': api.get('summary', ''),
                'parameters': api.get('parameters', [])
            }],
            'api_count': 1,
            'unified_schema': self._extract_single_schema(api),
            'lifecycle': self._infer_lifecycle([api])
        }

    def _create_capability(self, cluster_id: int, apis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a capability from a cluster of APIs with unified schema."""
        # Extract common tags
        all_tags = []
        for api in apis:
            all_tags.extend(api.get('tags', []))

        tag_counts = Counter(all_tags)
        primary_tag = tag_counts.most_common(1)[0][0] if tag_counts else f"capability_{cluster_id}"

        # Extract common action verbs
        action_verbs = [api.get('action_verb', '') for api in apis if api.get('action_verb')]
        primary_action = Counter(action_verbs).most_common(1)[0][0] if action_verbs else ''

        # Infer resource name from paths
        resource_name = self._infer_resource_name(apis)

        # Generate capability name
        capability_name = self._generate_capability_name(primary_tag, resource_name, primary_action)

        # Merge schemas from all APIs
        unified_schema = self._merge_schemas(apis)

        # Infer entity lifecycle
        lifecycle = self._infer_lifecycle(apis)

        # Calculate connectivity score
        connectivity = self._calculate_connectivity(apis, unified_schema)

        # Generate capability description
        description = self._generate_description(apis, resource_name, lifecycle)

        return {
            'id': f"cap_{cluster_id}",
            'name': capability_name,
            'type': 'composite',
            'description': description,
            'resource': resource_name,
            'primary_action': primary_action,
            'tags': list(tag_counts.keys()),
            'apis': [
                {
                    'operation_id': api['operation_id'],
                    'method': api['method'],
                    'path': api['path'],
                    'normalized_path': api.get('normalized_path', api['path']),
                    'summary': api.get('summary', ''),
                    'action_verb': api.get('action_verb', ''),
                    'parameters': api.get('parameters', [])
                }
                for api in apis
            ],
            'api_count': len(apis),
            'unified_schema': unified_schema,
            'lifecycle': lifecycle,
            'connectivity_score': connectivity,
            'typical_workflow': self._infer_workflow(apis, lifecycle)
        }

    def _extract_single_schema(self, api: Dict[str, Any]) -> Dict[str, Any]:
        """Extract schema from a single API."""
        schema = {
            'properties': {},
            'required': [],
            'read_only': [],
            'write_only': []
        }

        # Extract from request schema
        request_schema = api.get('request_schema') or {}
        if isinstance(request_schema, dict) and 'properties' in request_schema:
            for prop, prop_schema in request_schema['properties'].items():
                schema['properties'][prop] = prop_schema
                schema['write_only'].append(prop)
                if prop in request_schema.get('required', []):
                    schema['required'].append(prop)

        # Extract from response schemas
        response_schemas = api.get('response_schemas', {})
        for status, resp_schema in response_schemas.items():
            if status.startswith('2') and 'properties' in resp_schema:
                for prop, prop_schema in resp_schema['properties'].items():
                    if prop not in schema['properties']:
                        schema['properties'][prop] = prop_schema
                        schema['read_only'].append(prop)

        return schema

    def _merge_schemas(self, apis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Merge schemas from multiple APIs using entity lifecycle approach.

        Strategy:
        - Base Entity: Common fields across all operations
        - Create/Update specific: Fields that appear in write operations
        - Read specific: Fields that appear only in responses
        """
        all_properties = {}
        field_sources = defaultdict(set)  # Track which operations use each field
        field_required_in = defaultdict(set)  # Track where field is required
        field_read_only = set()
        field_write_only = set()

        for api in apis:
            method = api.get('method', '')
            operation_id = api.get('operation_id', '')

            # Process request schema
            request_schema = api.get('request_schema') or {}
            if isinstance(request_schema, dict) and 'properties' in request_schema:
                for prop, prop_schema in request_schema['properties'].items():
                    if prop not in all_properties:
                        all_properties[prop] = prop_schema
                    field_sources[prop].add(f"{method}_request")
                    field_write_only.add(prop)

                    if prop in request_schema.get('required', []):
                        field_required_in[prop].add(operation_id)

            # Process response schemas
            response_schemas = api.get('response_schemas', {})
            for status, resp_schema in response_schemas.items():
                if status.startswith('2') and 'properties' in resp_schema:
                    for prop, prop_schema in resp_schema['properties'].items():
                        if prop not in all_properties:
                            all_properties[prop] = prop_schema
                        else:
                            # Merge type information if conflict
                            all_properties[prop] = self._merge_property_schemas(
                                all_properties[prop], prop_schema
                            )
                        field_sources[prop].add(f"{method}_response")
                        if prop in field_write_only:
                            field_write_only.remove(prop)  # Appears in both
                        else:
                            field_read_only.add(prop)

        # Determine truly read-only and write-only fields
        truly_read_only = field_read_only - field_write_only
        truly_write_only = field_write_only - field_read_only

        # Determine required fields (required in ALL create operations)
        create_ops = [api for api in apis if api.get('method') == 'POST']
        required_fields = []
        if create_ops:
            # Field is required if it's required in all create operations
            for field, required_in_ops in field_required_in.items():
                if len(required_in_ops) >= len(create_ops):
                    required_fields.append(field)

        return {
            'properties': all_properties,
            'required': required_fields,
            'read_only': list(truly_read_only),
            'write_only': list(truly_write_only),
            'field_sources': {k: list(v) for k, v in field_sources.items()}
        }

    def _merge_property_schemas(self, schema1: Dict[str, Any], schema2: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two property schemas, resolving conflicts."""
        merged = schema1.copy()

        # If types differ, prefer more specific type
        type1 = schema1.get('type', 'string')
        type2 = schema2.get('type', 'string')

        if type1 != type2:
            # Prefer enum over string, integer over number, etc.
            if 'enum' in schema2:
                merged = schema2.copy()
            elif type2 in ['integer', 'boolean'] and type1 == 'string':
                merged['type'] = type2

        # Merge descriptions
        desc1 = schema1.get('description', '')
        desc2 = schema2.get('description', '')
        if desc2 and desc2 != desc1:
            merged['description'] = f"{desc1}; {desc2}" if desc1 else desc2

        return merged

    def _infer_resource_name(self, apis: List[Dict[str, Any]]) -> str:
        """Infer resource name from APIs, prioritizing entity_anchor."""
        # First, try to use entity_anchor if available (from entity clustering)
        entity_anchors = [api.get('entity_anchor') for api in apis if api.get('entity_anchor')]
        if entity_anchors:
            # Use the most common entity anchor
            anchor_counts = Counter(entity_anchors)
            most_common_anchor = anchor_counts.most_common(1)[0][0]
            if most_common_anchor and most_common_anchor != 'unknown':
                return most_common_anchor

        # Fallback: extract from path segments
        path_segments = []
        for api in apis:
            segments = api.get('path_segments', [])
            path_segments.extend(segments)

        if not path_segments:
            return 'Resource'

        # Count segment frequency
        segment_counts = Counter(path_segments)
        # Get most common non-generic segment
        for segment, count in segment_counts.most_common():
            if segment.lower() not in ['api', 'v1', 'v2', 'v3', 'admin', 'public']:
                return segment.capitalize()

        return 'Resource'

    def _generate_capability_name(self, tag: str, resource: str, action: str) -> str:
        """Generate a descriptive capability name based on entity."""
        # Clean up resource name for better readability
        resource_clean = resource.replace('-', ' ').replace('_', ' ').title()

        # If resource is generic, use tag
        if resource_clean.lower() in ['http', 'resource', 'api', 'unknown']:
            resource_clean = tag.replace('-', ' ').replace('_', ' ').title()

        # Generate concise name
        return f"{resource_clean} Management"

    def _infer_lifecycle(self, apis: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Infer entity lifecycle from available operations."""
        methods = {api.get('method') for api in apis}
        action_verbs = {api.get('action_verb', '').lower() for api in apis if api.get('action_verb')}

        lifecycle = {
            'has_create': 'POST' in methods or 'create' in action_verbs,
            'has_read': 'GET' in methods or 'get' in action_verbs or 'list' in action_verbs,
            'has_update': 'PUT' in methods or 'PATCH' in methods or 'update' in action_verbs,
            'has_delete': 'DELETE' in methods or 'delete' in action_verbs,
            'is_complete_crud': False
        }

        lifecycle['is_complete_crud'] = all([
            lifecycle['has_create'],
            lifecycle['has_read'],
            lifecycle['has_update'],
            lifecycle['has_delete']
        ])

        return lifecycle

    def _calculate_connectivity(self, apis: List[Dict[str, Any]], unified_schema: Dict[str, Any]) -> float:
        """
        Calculate connectivity score: how well APIs form a closed loop.

        Checks:
        - Do output fields of one API match input fields of another?
        - Is there a complete CRUD cycle?
        - Can workflows be chained?
        """
        score = 0.0
        max_score = 4.0

        # Check 1: CRUD completeness (0-1)
        lifecycle = self._infer_lifecycle(apis)
        crud_score = sum([
            0.3 if lifecycle['has_create'] else 0,
            0.2 if lifecycle['has_read'] else 0,
            0.3 if lifecycle['has_update'] else 0,
            0.2 if lifecycle['has_delete'] else 0
        ])
        score += crud_score

        # Check 2: Schema coverage (0-1)
        # Do we have both read and write operations?
        read_only = set(unified_schema.get('read_only', []))
        write_only = set(unified_schema.get('write_only', []))
        if read_only and write_only:
            score += 1.0
        elif read_only or write_only:
            score += 0.5

        # Check 3: Parameter chaining (0-1)
        # Can output of one API be input to another?
        has_chaining = self._check_parameter_chaining(apis)
        if has_chaining:
            score += 1.0

        # Check 4: Path consistency (0-1)
        # Do paths follow RESTful patterns?
        path_consistency = self._check_path_consistency(apis)
        score += path_consistency

        return round(score / max_score, 2)

    def _check_parameter_chaining(self, apis: List[Dict[str, Any]]) -> bool:
        """Check if APIs can be chained (output of one is input of another)."""
        # Collect all output fields (from responses)
        output_fields = set()
        for api in apis:
            response_schemas = api.get('response_schemas', {})
            for status, schema in response_schemas.items():
                if status.startswith('2') and 'properties' in schema:
                    output_fields.update(schema['properties'].keys())

        # Collect all input fields (from requests and path parameters)
        input_fields = set()
        for api in apis:
            # Request body fields
            request_schema = api.get('request_schema') or {}
            if isinstance(request_schema, dict) and 'properties' in request_schema:
                input_fields.update(request_schema['properties'].keys())

            # Path and query parameters
            params = api.get('parameters', {})
            if isinstance(params, dict):
                for param_type, param_list in params.items():
                    for param in param_list:
                        if isinstance(param, dict):
                            input_fields.add(param.get('name', ''))
            elif isinstance(params, list):
                for param in params:
                    if isinstance(param, dict):
                        input_fields.add(param.get('name', ''))

        # Check overlap
        overlap = output_fields & input_fields
        return len(overlap) > 0

    def _check_path_consistency(self, apis: List[Dict[str, Any]]) -> float:
        """Check if paths follow consistent RESTful patterns."""
        normalized_paths = [api.get('normalized_path', '') for api in apis]

        if not normalized_paths:
            return 0.0

        # Check if paths share common prefix
        common_prefix = self._find_common_prefix(normalized_paths)
        if len(common_prefix) > 1:
            return 1.0

        # Check if paths are related (share segments)
        all_segments = []
        for api in apis:
            all_segments.extend(api.get('path_segments', []))

        if len(set(all_segments)) < len(all_segments):
            # Has shared segments
            return 0.7

        return 0.3

    def _find_common_prefix(self, paths: List[str]) -> str:
        """Find common prefix among paths."""
        if not paths:
            return ''

        prefix = paths[0]
        for path in paths[1:]:
            while not path.startswith(prefix):
                prefix = prefix[:-1]
                if not prefix:
                    return ''

        return prefix

    def _infer_workflow(self, apis: List[Dict[str, Any]], lifecycle: Dict[str, Any]) -> str:
        """Infer typical workflow from available operations."""
        workflow_parts = []

        if lifecycle['has_create']:
            create_api = next((api for api in apis if api.get('method') == 'POST'), None)
            if create_api:
                workflow_parts.append(f"Create via {create_api.get('operation_id')}")

        if lifecycle['has_read']:
            read_api = next((api for api in apis if api.get('method') == 'GET'), None)
            if read_api:
                workflow_parts.append(f"Read via {read_api.get('operation_id')}")

        if lifecycle['has_update']:
            update_api = next((api for api in apis if api.get('method') in ['PUT', 'PATCH']), None)
            if update_api:
                workflow_parts.append(f"Update via {update_api.get('operation_id')}")

        if lifecycle['has_delete']:
            delete_api = next((api for api in apis if api.get('method') == 'DELETE'), None)
            if delete_api:
                workflow_parts.append(f"Delete via {delete_api.get('operation_id')}")

        return ' → '.join(workflow_parts) if workflow_parts else 'Single operation'

    def _generate_description(self, apis: List[Dict[str, Any]], resource: str, lifecycle: Dict[str, Any]) -> str:
        """Generate capability description."""
        operations = []
        if lifecycle['has_create']:
            operations.append('create')
        if lifecycle['has_read']:
            operations.append('query')
        if lifecycle['has_update']:
            operations.append('update')
        if lifecycle['has_delete']:
            operations.append('delete')

        ops_text = ', '.join(operations) if operations else 'manage'

        return f"Capability to {ops_text} {resource} resources. Includes {len(apis)} API endpoint(s)."
