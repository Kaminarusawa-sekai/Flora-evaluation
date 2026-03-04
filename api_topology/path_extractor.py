"""JSON Path support for nested fields."""

from typing import Dict, Any, List, Optional


class PathExtractor:
    """Extract and match nested field paths."""

    @staticmethod
    def flatten_schema(schema: Dict[str, Any], prefix: str = "") -> List[Dict[str, Any]]:
        """Flatten nested schema to field list with JSON paths."""
        fields = []

        if not isinstance(schema, dict):
            return fields

        properties = schema.get('properties', {})
        for name, prop in properties.items():
            path = f"{prefix}.{name}" if prefix else name
            field_type = prop.get('type', 'object')

            fields.append({
                'name': name,
                'path': path,
                'type': field_type,
                'description': prop.get('description', '')
            })

            # Recurse for nested objects
            if field_type == 'object' and 'properties' in prop:
                fields.extend(PathExtractor.flatten_schema(prop, path))

            # Handle arrays of objects
            elif field_type == 'array' and 'items' in prop:
                items = prop['items']
                if isinstance(items, dict) and items.get('type') == 'object':
                    array_path = f"{path}[]"
                    fields.extend(PathExtractor.flatten_schema(items, array_path))

        return fields

    @staticmethod
    def extract_leaf_name(path: str) -> str:
        """Extract leaf field name from path."""
        return path.split('.')[-1].replace('[]', '')

    @staticmethod
    def paths_compatible(source_path: str, target_path: str) -> bool:
        """Check if paths are structurally compatible."""
        # user.id -> id (compatible)
        # items[].id -> id (compatible)
        source_leaf = PathExtractor.extract_leaf_name(source_path)
        target_leaf = PathExtractor.extract_leaf_name(target_path)
        return source_leaf == target_leaf
