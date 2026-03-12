"""Swagger/OpenAPI document parser with enhanced features."""

import json
import yaml
import re
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
from urllib.parse import urlparse
from html import unescape


class SwaggerParser:
    """Parse Swagger/OpenAPI documents and extract API information."""

    def __init__(self, use_prance: bool = True):
        """
        Initialize parser.

        Args:
            use_prance: Whether to use prance for enhanced parsing (resolves $ref)
        """
        self.use_prance = use_prance
        self._prance_parser = None

    def parse(self, source) -> Dict[str, Any]:
        """
        Parse Swagger file, URL, or dict and return structured API data.

        Args:
            source: File path, URL to Swagger/OpenAPI document, or already loaded dict

        Returns:
            Structured API data with enhanced metadata
        """
        # If source is already a dict, use it directly
        if isinstance(source, dict):
            doc = source
        else:
            doc = self._load_document(source)

            # Use prance for enhanced parsing if available
            if self.use_prance and self._is_file_path(source):
                try:
                    import prance
                    parser = prance.ResolvingParser(source, lazy=True, strict=False)
                    doc = parser.specification
                except ImportError:
                    pass  # Fall back to basic parsing
                except Exception:
                    pass  # Fall back to basic parsing

        return self._extract_apis(doc)

    def _load_document(self, source: str) -> Dict[str, Any]:
        """Load document from file or URL."""
        if self._is_url(source):
            return self._load_from_url(source)
        else:
            return self._load_from_file(source)

    def _is_url(self, source: str) -> bool:
        """Check if source is a URL."""
        try:
            result = urlparse(source)
            return all([result.scheme, result.netloc])
        except:
            return False

    def _is_file_path(self, source: str) -> bool:
        """Check if source is a file path."""
        return not self._is_url(source)

    def _load_from_url(self, url: str) -> Dict[str, Any]:
        """Load Swagger document from URL (supports Apifox, etc.)."""
        try:
            # Handle common API documentation platforms
            if 'apifox.com' in url or 'apifox.cn' in url:
                # Apifox export URL pattern
                if '/api/v1/projects/' in url and '/export-openapi' not in url:
                    # Try to construct export URL
                    url = url.rstrip('/') + '/export-openapi'

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json, application/yaml, text/yaml, */*'
            }

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            content_type = response.headers.get('Content-Type', '')

            if 'yaml' in content_type or url.endswith(('.yaml', '.yml')):
                return yaml.safe_load(response.text)
            else:
                return response.json()

        except Exception as e:
            raise ValueError(f"Failed to load Swagger from URL {url}: {str(e)}")

    def _load_from_file(self, file_path: str) -> Dict[str, Any]:
        """Load Swagger document from file."""
        path = Path(file_path)

        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)

    def _extract_apis(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Extract API endpoints with enhanced metadata."""
        apis = []
        base_path = doc.get('basePath', '')

        # Support both OpenAPI 2.0 and 3.0
        servers = doc.get('servers', [])
        if servers and not base_path:
            base_path = servers[0].get('url', '')

        for path, methods in doc.get('paths', {}).items():
            for method, details in methods.items():
                if method.upper() not in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']:
                    continue

                # Normalize path (template parameters)
                normalized_path = self._normalize_path(base_path + path)

                # Extract action verb from operationId
                operation_id = details.get('operationId', f"{method}_{path}")
                action_verb = self._extract_action_verb(operation_id)

                # Clean description
                description = self._clean_description(details.get('description', ''))
                summary = self._clean_description(details.get('summary', ''))

                # Extract parameters with type classification
                parameters = self._extract_parameters_enhanced(details, doc)

                # Extract request/response schemas
                request_schema = self._extract_request_schema(details, doc)
                response_schemas = self._extract_response_schemas(details, doc)

                api = {
                    'path': base_path + path,
                    'normalized_path': normalized_path,
                    'path_segments': self._extract_path_segments(normalized_path),
                    'method': method.upper(),
                    'operation_id': operation_id,
                    'action_verb': action_verb,
                    'summary': summary,
                    'description': description,
                    'tags': details.get('tags', []),
                    'parameters': parameters,
                    'request_schema': request_schema,
                    'response_schemas': response_schemas,
                    'responses': list(details.get('responses', {}).keys())
                }
                apis.append(api)

        return {
            'title': doc.get('info', {}).get('title', 'API'),
            'version': doc.get('info', {}).get('version', '1.0'),
            'description': doc.get('info', {}).get('description', ''),
            'apis': apis
        }

    def _normalize_path(self, path: str) -> str:
        """
        Normalize path by converting actual IDs to template parameters.
        E.g., /user/123/order/456 -> /user/{id}/order/{id}
        """
        # Replace UUID-like patterns first (more specific)
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{uuid}', path, flags=re.IGNORECASE)
        # Replace numeric IDs (less specific)
        path = re.sub(r'/\d+', '/{id}', path)
        return path

    def _extract_path_segments(self, path: str) -> List[str]:
        """Extract meaningful path segments (excluding parameters)."""
        segments = []
        for segment in path.split('/'):
            if segment and not segment.startswith('{'):
                segments.append(segment)
        return segments

    def _extract_action_verb(self, operation_id: str) -> Optional[str]:
        """
        Extract action verb from operationId.
        E.g., 'syncUserData' -> 'sync', 'batchCreateOrders' -> 'batch'
        """
        # Common action verbs
        action_verbs = [
            'sync', 'batch', 'export', 'import', 'upload', 'download',
            'create', 'update', 'delete', 'get', 'list', 'search',
            'query', 'fetch', 'save', 'remove', 'add', 'modify'
        ]

        operation_lower = operation_id.lower()
        for verb in action_verbs:
            if operation_lower.startswith(verb):
                return verb

        return None

    def _clean_description(self, text: str) -> str:
        """
        Clean description text by removing HTML tags and normalizing whitespace.
        """
        if not text or text.lower() in ['no description', 'none', 'n/a']:
            return ''

        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        # Unescape HTML entities
        text = unescape(text)
        # Normalize whitespace
        text = ' '.join(text.split())

        return text.strip()

    def _extract_parameters_enhanced(self, details: Dict[str, Any], doc: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract parameters with type classification (path, query, body, header).
        """
        params_by_type = {
            'path': [],
            'query': [],
            'body': [],
            'header': []
        }

        # OpenAPI 2.0 style
        for param in details.get('parameters', []):
            param_in = param.get('in', 'query')
            param_info = {
                'name': param.get('name', ''),
                'type': param.get('type', param.get('schema', {}).get('type', 'string')),
                'required': param.get('required', False),
                'description': self._clean_description(param.get('description', ''))
            }

            if param_in in params_by_type:
                params_by_type[param_in].append(param_info)

        # OpenAPI 3.0 style - requestBody
        request_body = details.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            for content_type, content_details in content.items():
                schema = content_details.get('schema', {})
                params_by_type['body'].append({
                    'content_type': content_type,
                    'schema': schema,
                    'required': request_body.get('required', False)
                })

        return params_by_type

    def _extract_request_schema(self, details: Dict[str, Any], doc: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract request body schema."""
        # OpenAPI 3.0
        request_body = details.get('requestBody', {})
        if request_body:
            content = request_body.get('content', {})
            for content_type, content_details in content.items():
                return content_details.get('schema')

        # OpenAPI 2.0
        for param in details.get('parameters', []):
            if param.get('in') == 'body':
                return param.get('schema')

        return None

    def _extract_response_schemas(self, details: Dict[str, Any], doc: Dict[str, Any]) -> Dict[str, Any]:
        """Extract response schemas for different status codes."""
        schemas = {}

        for status_code, response in details.get('responses', {}).items():
            # OpenAPI 3.0
            content = response.get('content', {})
            if content:
                for content_type, content_details in content.items():
                    schema = content_details.get('schema')
                    if schema:
                        schemas[status_code] = schema
                        break

            # OpenAPI 2.0
            schema = response.get('schema')
            if schema:
                schemas[status_code] = schema

        return schemas

    def _extract_parameters(self, details: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract parameter information (legacy method for compatibility)."""
        params = []
        for param in details.get('parameters', []):
            params.append({
                'name': param.get('name', ''),
                'in': param.get('in', ''),
                'type': param.get('type', param.get('schema', {}).get('type', 'string')),
                'required': param.get('required', False)
            })
        return params
