"""Main service interface for scenario generation."""

from typing import List, Dict, Any, Literal
from scenario_generator import ScenarioGenerator
from scenario_validator import ScenarioValidator


class ScenarioGenerationService:
    """Service for generating test scenarios from API paths."""

    def __init__(self, llm_config: Dict[str, Any] = None, api_topology: Dict[str, Any] = None):
        self.generator = ScenarioGenerator(llm_config)
        self.validator = ScenarioValidator(api_topology)

    def generate_scenarios(self, api_path: List[str],
                          api_details: Dict[str, Dict[str, Any]] = None,
                          parameter_flow: Dict[str, Any] = None,
                          scenario_types: List[str] = None,
                          count_per_type: int = 1) -> List[Dict[str, Any]]:
        """
        Generate test scenarios from an API execution path.

        Args:
            api_path: List of operation_ids representing an API call sequence
            api_details: Optional dict mapping operation_id to API details
            parameter_flow: Optional parameter dependency information from topology
            scenario_types: Types of scenarios to generate (default: ['normal', 'exception'])
            count_per_type: Number of scenarios per type

        Returns:
            List of generated scenarios with validation results
        """
        if scenario_types is None:
            scenario_types = ['normal', 'exception']

        scenarios = []

        for scenario_type in scenario_types:
            for i in range(count_per_type):
                scenario = self.generator.generate(
                    api_path, api_details, scenario_type, parameter_flow
                )

                validation = self.validator.validate(scenario, api_path, api_details)

                scenarios.append({
                    'scenario': scenario,
                    'validation': validation,
                    'api_path': api_path
                })

        return scenarios
