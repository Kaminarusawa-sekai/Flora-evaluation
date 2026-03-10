"""LLM-based intelligent entity relationship inference."""

from typing import Dict, List, Set, Optional, Any
import json


class LLMEntityInferrer:
    """
    Use LLM to intelligently infer entity relationships.

    This is the highest priority inference method when LLM is available.
    """

    def __init__(self, llm_client=None, max_entities_per_call: int = 10,
                 enable_fallback: bool = True):
        """
        Initialize LLM inferrer.

        Args:
            llm_client: LLM client (e.g., OpenAI, Anthropic)
            max_entities_per_call: Maximum entities to analyze per LLM call
            enable_fallback: Auto-fallback to other methods if LLM fails
        """
        self.llm_client = llm_client
        self.max_entities_per_call = max_entities_per_call
        self.relationship_cache = {}  # Cache LLM results
        self.enable_fallback = enable_fallback
        self.llm_failed = False  # Track if LLM has failed

    def infer_dependencies(self, api_map: Dict[str, Dict],
                          entity_groups: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
        """
        Use LLM to infer entity relationships.

        Args:
            api_map: Dict of operation_id -> api_data
            entity_groups: Dict of entity -> list of APIs

        Returns:
            List of dependency dicts with source, target, score, and type
        """
        if not self.llm_client:
            return []

        # Skip LLM if it has failed before and fallback is enabled
        if self.llm_failed and self.enable_fallback:
            print("  [LLM] Skipping - previous failure, using fallback methods")
            return []

        dependencies = []

        # Step 1: Get entity relationship map from LLM
        entity_relationships = self._get_entity_relationships_from_llm(entity_groups)

        # If LLM failed and returned empty, mark it
        if not entity_relationships and self.enable_fallback:
            self.llm_failed = True
            print("  [LLM] Failed - falling back to other inference methods")
            return []

        # Step 2: Create dependencies based on LLM suggestions
        for source_entity, related_entities in entity_relationships.items():
            if source_entity not in entity_groups:
                continue

            source_apis = entity_groups[source_entity]

            for target_entity, confidence in related_entities:
                if target_entity not in entity_groups:
                    continue

                target_apis = entity_groups[target_entity]

                # Create dependencies between write operations and read operations
                write_ops = [api for api in source_apis
                            if self._is_write_operation(api)]
                read_ops = [api for api in target_apis
                           if self._is_read_operation(api)]

                for source_api in write_ops:
                    for target_api in read_ops:
                        dependencies.append({
                            'source': source_api['operation_id'],
                            'target': target_api['operation_id'],
                            'score': confidence,
                            'type': 'LLM_INFERENCE',
                            'reason': f"LLM inferred: {source_entity} depends on {target_entity}"
                        })

        return dependencies

    def _get_entity_relationships_from_llm(self,
                                          entity_groups: Dict[str, List[Dict]]) -> Dict[str, List[tuple]]:
        """
        Ask LLM to infer entity relationships.

        Returns:
            Dict of entity -> [(related_entity, confidence), ...]
        """
        entities = list(entity_groups.keys())

        if not entities:
            return {}

        # Check cache
        cache_key = tuple(sorted(entities))
        if cache_key in self.relationship_cache:
            return self.relationship_cache[cache_key]

        # Prepare entity information for LLM
        entity_info = self._prepare_entity_info(entity_groups)

        # Build prompt
        prompt = self._build_relationship_prompt(entity_info)

        try:
            # Call LLM
            response = self._call_llm(prompt)

            # Parse response
            relationships = self._parse_llm_response(response)

            # Check if response is valid
            if not relationships:
                print(f"  [LLM] Warning: Empty response from LLM")
                if self.enable_fallback:
                    self.llm_failed = True
                return {}

            # Cache result
            self.relationship_cache[cache_key] = relationships

            return relationships

        except Exception as e:
            print(f"  [LLM] Error: {e}")
            if self.enable_fallback:
                self.llm_failed = True
                print(f"  [LLM] Auto-fallback enabled - will use other inference methods")
            return {}

    def _prepare_entity_info(self, entity_groups: Dict[str, List[Dict]]) -> Dict[str, Dict]:
        """
        Prepare entity information for LLM analysis.

        Returns:
            Dict of entity -> {operations, sample_fields}
        """
        entity_info = {}

        for entity, apis in entity_groups.items():
            # Get operations
            operations = set()
            for api in apis:
                op_type = self._get_operation_type(api)
                operations.add(op_type)

            # Get sample fields from first API
            sample_fields = set()
            if apis:
                first_api = apis[0]
                # Request fields
                request_schema = first_api.get('request_schema', {})
                sample_fields.update(self._extract_field_names(request_schema))

                # Response fields
                response_schemas = first_api.get('response_schemas', {})
                for schema in response_schemas.values():
                    sample_fields.update(self._extract_field_names(schema))

            entity_info[entity] = {
                'operations': list(operations),
                'sample_fields': list(sample_fields)[:10]  # Limit to 10 fields
            }

        return entity_info

    def _build_relationship_prompt(self, entity_info: Dict[str, Dict]) -> str:
        """
        Build prompt for LLM to infer entity relationships.
        """
        prompt = """You are an API architecture expert. Analyze the following entities and their operations to infer relationships.

Entities and their information:
"""

        for entity, info in entity_info.items():
            prompt += f"\n{entity}:"
            prompt += f"\n  Operations: {', '.join(info['operations'])}"
            if info['sample_fields']:
                prompt += f"\n  Sample fields: {', '.join(info['sample_fields'])}"

        prompt += """

Task: Identify which entities depend on which other entities. For example:
- If "order" has fields like "customerId" or "productId", it depends on "customer" and "product"
- If "payment" has "orderId", it depends on "order"
- If "order-item" is a sub-entity of "order", it depends on "order"

Return a JSON object where keys are source entities and values are lists of [target_entity, confidence_score].
Confidence score should be between 0.7 and 1.0.

Example output:
{
  "order": [["customer", 0.9], ["product", 0.9]],
  "payment": [["order", 0.95]],
  "order-item": [["order", 0.95], ["product", 0.85]]
}

Only include relationships you are confident about. Return only the JSON object, no explanation.
"""

        return prompt

    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM with the prompt.

        Supports multiple LLM clients (OpenAI, Anthropic, etc.)
        """
        if not self.llm_client:
            raise ValueError("No LLM client provided")

        # Try different LLM client types
        try:
            # OpenAI-style client (also works with Qwen, DeepSeek, etc.)
            if hasattr(self.llm_client, 'chat') and hasattr(self.llm_client.chat, 'completions'):
                # Try to detect model from client or use default
                model = getattr(self.llm_client, 'default_model', None)
                if not model:
                    # Auto-detect based on base_url
                    base_url = getattr(self.llm_client, 'base_url', '')
                    if 'dashscope' in str(base_url):
                        model = "qwen-plus"  # Qwen
                    elif 'deepseek' in str(base_url):
                        model = "deepseek-chat"  # DeepSeek
                    else:
                        model = "gpt-4"  # Default to GPT-4

                response = self.llm_client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are an API architecture expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    timeout=30  # 30 second timeout
                )
                return response.choices[0].message.content

            # Anthropic-style client
            elif hasattr(self.llm_client, 'messages') and hasattr(self.llm_client.messages, 'create'):
                response = self.llm_client.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=2000,
                    temperature=0.3,
                    timeout=30,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text

            # Generic client with __call__
            elif callable(self.llm_client):
                return self.llm_client(prompt)

            else:
                raise ValueError("Unsupported LLM client type")

        except Exception as e:
            # Re-raise to be caught by caller
            raise Exception(f"LLM API call failed: {str(e)}")

    def _parse_llm_response(self, response: str) -> Dict[str, List[tuple]]:
        """
        Parse LLM response to extract entity relationships.

        Returns:
            Dict of entity -> [(related_entity, confidence), ...]
        """
        try:
            # Extract JSON from response (handle markdown code blocks)
            response = response.strip()
            if response.startswith("```"):
                # Remove markdown code block
                lines = response.split('\n')
                response = '\n'.join(lines[1:-1])

            # Parse JSON
            relationships_raw = json.loads(response)

            # Convert to expected format
            relationships = {}
            for entity, related_list in relationships_raw.items():
                relationships[entity] = [
                    (related_entity, confidence)
                    for related_entity, confidence in related_list
                ]

            return relationships

        except Exception as e:
            print(f"Failed to parse LLM response: {e}")
            return {}

    def _extract_field_names(self, schema: Dict[str, Any], depth: int = 0) -> Set[str]:
        """Extract field names from schema."""
        if depth > 2 or not schema:
            return set()

        fields = set()

        # Get properties
        properties = schema.get('properties', {})
        for field_name in properties.keys():
            fields.add(field_name.lower())

        # Handle array items
        if schema.get('type') == 'array':
            items = schema.get('items', {})
            fields.update(self._extract_field_names(items, depth + 1))

        return fields

    def _is_write_operation(self, api: Dict) -> bool:
        """Check if API is a write operation (CREATE/UPDATE)."""
        method = api.get('method', '').upper()
        path = api.get('path', '').lower()

        return (method in ['POST', 'PUT', 'PATCH'] or
                '/create' in path or '/update' in path)

    def _is_read_operation(self, api: Dict) -> bool:
        """Check if API is a read operation (GET/LIST)."""
        method = api.get('method', '').upper()
        path = api.get('path', '').lower()

        return (method == 'GET' or
                '/get' in path or '/list' in path or '/page' in path)

    def _get_operation_type(self, api: Dict) -> str:
        """Get operation type from API."""
        path = api.get('path', '').lower()
        method = api.get('method', '').upper()

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
