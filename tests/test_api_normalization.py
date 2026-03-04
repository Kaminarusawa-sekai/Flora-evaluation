"""
Unit tests for api_normalization module.
"""

import pytest
import json
from pathlib import Path
from api_normalization import NormalizationService
from api_normalization.swagger_parser import SwaggerParser
from api_normalization.semantic_clusterer import SemanticClusterer
from api_normalization.capability_extractor import CapabilityExtractor


class TestSwaggerParser:
    """Test SwaggerParser functionality."""

    def test_parse_json(self, tmp_path):
        """Test parsing JSON Swagger file."""
        swagger_file = tmp_path / "test.json"
        swagger_data = {
            "swagger": "2.0",
            "info": {"title": "Test API", "version": "1.0"},
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "getUsers",
                        "summary": "Get users",
                        "tags": ["users"]
                    }
                }
            }
        }
        swagger_file.write_text(json.dumps(swagger_data))

        parser = SwaggerParser()
        result = parser.parse(str(swagger_file))

        assert result['title'] == "Test API"
        assert result['version'] == "1.0"
        assert len(result['apis']) == 1
        assert result['apis'][0]['operation_id'] == "getUsers"


class TestSemanticClusterer:
    """Test SemanticClusterer functionality."""

    def test_cluster_apis(self):
        """Test API clustering."""
        apis = [
            {
                'operation_id': 'createUser',
                'method': 'POST',
                'path': '/users',
                'summary': 'Create user',
                'tags': ['users']
            },
            {
                'operation_id': 'getUser',
                'method': 'GET',
                'path': '/users/{id}',
                'summary': 'Get user',
                'tags': ['users']
            },
            {
                'operation_id': 'createOrder',
                'method': 'POST',
                'path': '/orders',
                'summary': 'Create order',
                'tags': ['orders']
            }
        ]

        clusterer = SemanticClusterer()
        result = clusterer.cluster(apis)

        assert len(result) == 3
        assert all('cluster' in api for api in result)


class TestCapabilityExtractor:
    """Test CapabilityExtractor functionality."""

    def test_extract_capabilities(self):
        """Test capability extraction."""
        apis = [
            {
                'operation_id': 'createUser',
                'method': 'POST',
                'path': '/users',
                'summary': 'Create user',
                'tags': ['users'],
                'cluster': 0
            },
            {
                'operation_id': 'getUser',
                'method': 'GET',
                'path': '/users/{id}',
                'summary': 'Get user',
                'tags': ['users'],
                'cluster': 0
            }
        ]

        extractor = CapabilityExtractor()
        result = extractor.extract(apis)

        assert 'capabilities' in result
        assert result['total_apis'] == 2
        assert result['total_capabilities'] >= 1


class TestNormalizationService:
    """Test NormalizationService integration."""

    def test_normalize_swagger(self, tmp_path):
        """Test end-to-end normalization."""
        swagger_file = tmp_path / "test.json"
        swagger_data = {
            "swagger": "2.0",
            "info": {"title": "Test API", "version": "1.0"},
            "paths": {
                "/users": {
                    "post": {
                        "operationId": "createUser",
                        "summary": "Create user",
                        "tags": ["users"]
                    }
                }
            }
        }
        swagger_file.write_text(json.dumps(swagger_data))

        service = NormalizationService()
        result = service.normalize_swagger(str(swagger_file))

        assert 'capabilities' in result
        assert 'source' in result
        assert result['source']['title'] == "Test API"
