"""Detect complex field transformations."""

from typing import Dict, Any, Optional


class TransformationDetector:
    """Detect fields requiring logical transformations."""

    # Patterns indicating transformation needed
    TRANSFORM_PATTERNS = {
        'sign': ['signature', 'sign', 'hash', 'checksum'],
        'encrypt': ['encrypted', 'cipher', 'encoded'],
        'aggregate': ['total', 'sum', 'count', 'average'],
        'format': ['formatted', 'display', 'rendered']
    }

    @staticmethod
    def detect_transformation(source_field: Dict[str, Any],
                            target_field: Dict[str, Any]) -> Optional[str]:
        """Detect if transformation is needed between fields."""
        source_name = source_field['name'].lower()
        target_name = target_field['name'].lower()
        target_desc = target_field.get('description', '').lower()

        # Check for transformation keywords
        for transform_type, keywords in TransformationDetector.TRANSFORM_PATTERNS.items():
            if any(kw in target_name or kw in target_desc for kw in keywords):
                return transform_type

        # Array to single value
        if source_field.get('type') == 'array' and target_field.get('type') != 'array':
            return 'aggregate'

        # Type mismatch requiring conversion
        source_type = source_field.get('type')
        target_type = target_field.get('type')
        if source_type != target_type and source_type and target_type:
            return 'convert'

        return None
