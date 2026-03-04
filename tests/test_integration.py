"""
Integration tests for all four service modules.
"""

import pytest
import json
from pathlib import Path
from api_normalization import NormalizationService
from scenario_generation import ScenarioGenerationService


class TestEndToEndWorkflow:
    """Test complete workflow using all services."""

    def test_normalization_to_scenario_generation(self, tmp_path):
        """Test workflow from Swagger parsing to scenario generation."""
        # Create test Swagger file
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
                },
                "/users/{id}": {
                    "get": {
                        "operationId": "getUser",
                        "summary": "Get user",
                        "tags": ["users"],
                        "parameters": [{"name": "id", "in": "path", "type": "string"}]
                    },
                    "delete": {
                        "operationId": "deleteUser",
                        "summary": "Delete user",
                        "tags": ["users"],
                        "parameters": [{"name": "id", "in": "path", "type": "string"}]
                    }
                }
            }
        }
        swagger_file.write_text(json.dumps(swagger_data))

        # Step 1: Normalize Swagger
        norm_service = NormalizationService()
        capabilities = norm_service.normalize_swagger(str(swagger_file))

        assert 'capabilities' in capabilities
        assert capabilities['total_apis'] == 3

        # Step 2: Generate scenarios from API path
        scenario_service = ScenarioGenerationService()
        api_path = ['createUser', 'getUser', 'deleteUser']

        scenarios = scenario_service.generate_scenarios(api_path, count=2)

        assert len(scenarios) == 2
        for result in scenarios:
            assert result['validation']['is_valid'] is True
            assert len(result['scenario']['steps']) == 3
