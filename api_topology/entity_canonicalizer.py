"""LLM-based entity canonicalization."""

from typing import Dict, Any, Optional, List
import json


class EntityCanonicalizer:
    """Map fields to standard entities using LLM."""

    # Standard entity types
    ENTITIES = {
        'USER_ID', 'ORDER_ID', 'PRODUCT_ID', 'TOKEN', 'EMAIL',
        'PHONE', 'ADDRESS', 'TIMESTAMP', 'AMOUNT', 'STATUS'
    }

    def __init__(self, llm_client=None):
        self.llm_client = llm_client
        self._cache = {}

    def canonicalize_field(self, field: Dict[str, Any], api_context: str = "") -> Optional[str]:
        """Map field to standard entity."""
        cache_key = f"{field['name']}:{field.get('type')}:{api_context}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self.llm_client:
            # Fallback to rule-based
            entity = self._rule_based_mapping(field)
        else:
            entity = self._llm_mapping(field, api_context)

        self._cache[cache_key] = entity
        return entity

    def _rule_based_mapping(self, field: Dict[str, Any]) -> Optional[str]:
        """Simple rule-based entity mapping."""
        name = field['name'].lower().replace('_', '').replace('-', '')

        if 'userid' in name or 'uid' in name:
            return 'USER_ID'
        elif 'orderid' in name:
            return 'ORDER_ID'
        elif 'productid' in name or 'pid' in name:
            return 'PRODUCT_ID'
        elif 'token' in name or 'accesstoken' in name:
            return 'TOKEN'
        elif 'email' in name:
            return 'EMAIL'
        elif 'phone' in name or 'mobile' in name:
            return 'PHONE'
        elif 'address' in name:
            return 'ADDRESS'
        elif 'time' in name or 'date' in name:
            return 'TIMESTAMP'
        elif 'amount' in name or 'price' in name:
            return 'AMOUNT'
        elif 'status' in name or 'state' in name:
            return 'STATUS'

        return None

    def _llm_mapping(self, field: Dict[str, Any], api_context: str) -> Optional[str]:
        """Use LLM to map field to entity."""
        prompt = f"""Map this API field to a standard entity type.

Field: {field['name']}
Type: {field.get('type', 'unknown')}
Description: {field.get('description', 'N/A')}
API Context: {api_context}

Standard entities: {', '.join(self.ENTITIES)}

Return ONLY the entity name or 'NONE'. Example: USER_ID"""

        try:
            response = self.llm_client.generate(prompt, max_tokens=20)
            entity = response.strip().upper()
            return entity if entity in self.ENTITIES else None
        except:
            return self._rule_based_mapping(field)

    def fields_match_by_entity(self, field1: Dict[str, Any], field2: Dict[str, Any],
                               context1: str = "", context2: str = "") -> bool:
        """Check if two fields map to same entity."""
        entity1 = self.canonicalize_field(field1, context1)
        entity2 = self.canonicalize_field(field2, context2)
        return entity1 is not None and entity1 == entity2
