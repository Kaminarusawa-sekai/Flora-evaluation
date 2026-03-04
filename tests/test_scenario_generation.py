"""
Unit tests for scenario_generation module.
"""

import pytest
from scenario_generation import ScenarioGenerationService
from scenario_generation.scenario_generator import ScenarioGenerator
from scenario_generation.scenario_validator import ScenarioValidator


class TestScenarioGenerator:
    """Test ScenarioGenerator functionality."""

    def test_generate_scenario(self):
        """Test scenario generation."""
        generator = ScenarioGenerator()
        api_path = ['createUser', 'getUser', 'deleteUser']

        scenario = generator.generate(api_path)

        assert 'title' in scenario
        assert 'description' in scenario
        assert 'steps' in scenario
        assert 'expected_outcome' in scenario
        assert len(scenario['steps']) == 3


class TestScenarioValidator:
    """Test ScenarioValidator functionality."""

    def test_validate_valid_scenario(self):
        """Test validation of valid scenario."""
        validator = ScenarioValidator()
        scenario = {
            'title': 'User Management Test',
            'description': 'Test user creation and deletion workflow',
            'steps': ['Create user', 'Get user', 'Delete user'],
            'expected_outcome': 'User should be created and deleted successfully'
        }
        api_path = ['createUser', 'getUser', 'deleteUser']

        result = validator.validate(scenario, api_path)

        assert result['is_valid'] is True
        assert len(result['issues']) == 0

    def test_validate_invalid_scenario(self):
        """Test validation of invalid scenario."""
        validator = ScenarioValidator()
        scenario = {
            'title': 'Test'
        }
        api_path = ['createUser']

        result = validator.validate(scenario, api_path)

        assert result['is_valid'] is False
        assert len(result['issues']) > 0


class TestScenarioGenerationService:
    """Test ScenarioGenerationService integration."""

    def test_generate_scenarios(self):
        """Test end-to-end scenario generation."""
        service = ScenarioGenerationService()
        api_path = ['createUser', 'getUser']

        scenarios = service.generate_scenarios(api_path, count=2)

        assert len(scenarios) == 2
        for result in scenarios:
            assert 'scenario' in result
            assert 'validation' in result
            assert 'api_path' in result
