"""Entity-based dependency inference for API topology."""

from typing import Dict, List, Set, Tuple
import re


class EntityDependencyInferrer:
    """
    Infer API dependencies based on entity relationships and business logic.

    This complements field-based matching when API descriptions are missing.
    """

    # Common entity relationship patterns in ERP/CRM systems
    ENTITY_RELATIONSHIPS = {
        # Purchase flow
        'purchase-order': ['supplier', 'product', 'account'],
        'purchase-in': ['purchase-order', 'warehouse', 'product'],
        'purchase-return': ['purchase-in', 'supplier', 'product'],

        # Sale flow
        'sale-order': ['customer', 'product', 'account'],
        'sale-out': ['sale-order', 'warehouse', 'product'],
        'sale-return': ['sale-out', 'customer', 'product'],

        # Stock management
        'stock': ['warehouse', 'product'],
        'stock-in': ['warehouse', 'product'],
        'stock-out': ['warehouse', 'product'],
        'stock-move': ['warehouse', 'product'],
        'stock-check': ['warehouse', 'product'],
        'stock-record': ['warehouse', 'product', 'stock'],

        # Finance
        'finance-payment': ['supplier', 'account', 'purchase-order'],
        'finance-receipt': ['customer', 'account', 'sale-order'],
        'bookkeeping-voucher': ['account'],

        # Product hierarchy
        'product': ['product-category', 'product-unit', 'supplier'],
        'product-category': [],
        'product-unit': [],

        # Basic entities
        'supplier': [],
        'customer': [],
        'warehouse': [],
        'account': [],
    }

    # CRUD operation priorities (for dependency direction)
    OPERATION_PRIORITY = {
        'create': 1,  # Creates data
        'get': 2,     # Reads single item
        'page': 2,    # Reads list
        'list': 2,    # Reads list
        'update': 3,  # Modifies data
        'delete': 4,  # Removes data
    }

    def __init__(self):
        """Initialize the inferrer."""
        pass

    def infer_dependencies(self, api_map: Dict[str, Dict]) -> List[Dict[str, any]]:
        """
        Infer dependencies based on entity relationships.

        Args:
            api_map: Dict of operation_id -> api_data (with entity info)

        Returns:
            List of dependency dicts with source, target, score, and type
        """
        dependencies = []

        # Group APIs by entity
        entity_groups = self._group_by_entity(api_map)

        # Infer cross-entity dependencies
        for source_entity, source_apis in entity_groups.items():
            # Get related entities
            related_entities = self.ENTITY_RELATIONSHIPS.get(source_entity, [])

            for related_entity in related_entities:
                if related_entity not in entity_groups:
                    continue

                target_apis = entity_groups[related_entity]

                # Create dependencies between operations
                deps = self._create_entity_dependencies(
                    source_entity, source_apis,
                    related_entity, target_apis
                )
                dependencies.extend(deps)

        # Infer intra-entity dependencies (CRUD flow)
        for entity, apis in entity_groups.items():
            deps = self._create_crud_dependencies(entity, apis)
            dependencies.extend(deps)

        return dependencies

    def _group_by_entity(self, api_map: Dict[str, Dict]) -> Dict[str, List[Dict]]:
        """Group APIs by their entity."""
        groups = {}

        for op_id, api in api_map.items():
            entity = api.get('entity', api.get('resource', 'unknown'))
            if entity not in groups:
                groups[entity] = []
            groups[entity].append({
                'operation_id': op_id,
                **api
            })

        return groups

    def _create_entity_dependencies(self,
                                   source_entity: str, source_apis: List[Dict],
                                   target_entity: str, target_apis: List[Dict]) -> List[Dict]:
        """
        Create dependencies between two related entities.

        Logic:
        - Source entity's CREATE/UPDATE operations depend on target entity's GET/LIST
        - Example: createPurchaseOrder depends on getSupplier, listProduct
        """
        dependencies = []

        # Find source operations that need target data
        source_write_ops = [api for api in source_apis
                           if self._get_operation_type(api) in ['create', 'update']]

        # Find target operations that provide data
        target_read_ops = [api for api in target_apis
                          if self._get_operation_type(api) in ['get', 'page', 'list']]

        for source_api in source_write_ops:
            for target_api in target_read_ops:
                dependencies.append({
                    'source': source_api['operation_id'],
                    'target': target_api['operation_id'],
                    'score': 0.7,  # Entity-based inference score
                    'type': 'ENTITY_RELATION',
                    'reason': f"{source_entity} requires {target_entity} data"
                })

        return dependencies

    def _create_crud_dependencies(self, entity: str, apis: List[Dict]) -> List[Dict]:
        """
        Create dependencies within CRUD operations of the same entity.

        Logic:
        - UPDATE depends on GET (need to fetch before update)
        - DELETE depends on GET (need to verify before delete)
        - GET/LIST are independent
        """
        dependencies = []

        # Group by operation type
        ops_by_type = {}
        for api in apis:
            op_type = self._get_operation_type(api)
            if op_type not in ops_by_type:
                ops_by_type[op_type] = []
            ops_by_type[op_type].append(api)

        # UPDATE depends on GET
        if 'update' in ops_by_type and 'get' in ops_by_type:
            for update_api in ops_by_type['update']:
                for get_api in ops_by_type['get']:
                    dependencies.append({
                        'source': update_api['operation_id'],
                        'target': get_api['operation_id'],
                        'score': 0.8,
                        'type': 'CRUD_FLOW',
                        'reason': f"Update {entity} requires fetching current data"
                    })

        # DELETE depends on GET
        if 'delete' in ops_by_type and 'get' in ops_by_type:
            for delete_api in ops_by_type['delete']:
                for get_api in ops_by_type['get']:
                    dependencies.append({
                        'source': delete_api['operation_id'],
                        'target': get_api['operation_id'],
                        'score': 0.6,
                        'type': 'CRUD_FLOW',
                        'reason': f"Delete {entity} may require verification"
                    })

        return dependencies

    def _get_operation_type(self, api: Dict) -> str:
        """
        Extract operation type from API path or method.

        Returns: 'create', 'get', 'page', 'list', 'update', 'delete', or 'other'
        """
        path = api.get('path', '').lower()
        method = api.get('method', '').upper()

        # Check path for operation hints
        if '/create' in path or method == 'POST':
            return 'create'
        elif '/update' in path or method in ['PUT', 'PATCH']:
            return 'update'
        elif '/delete' in path or method == 'DELETE':
            return 'delete'
        elif '/page' in path:
            return 'page'
        elif '/list' in path:
            return 'list'
        elif '/get' in path or '/{id}' in path or method == 'GET':
            return 'get'

        return 'other'

    def filter_high_confidence_dependencies(self,
                                           dependencies: List[Dict],
                                           min_score: float = 0.6) -> List[Dict]:
        """Filter dependencies by confidence score."""
        return [dep for dep in dependencies if dep['score'] >= min_score]
