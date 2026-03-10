"""Validate generated test scenarios."""

from typing import Dict, Any, List, Optional


class ScenarioValidator:
    """Validate test scenario quality and completeness with enhanced logic checks."""

    def __init__(self, api_topology: Optional[Dict[str, Any]] = None):
        """Initialize validator with optional API topology for path validation."""
        self.api_topology = api_topology

    def validate(self, scenario: Dict[str, Any], api_path: List[str],
                 api_details: Optional[Dict[str, Dict[str, Any]]] = None) -> Dict[str, Any]:
        """Validate a generated scenario with enhanced checks."""
        issues = []
        warnings = []

        # Basic field checks
        required_fields = ['title', 'description', 'steps', 'expected_outcome', 'scenario_type']
        for field in required_fields:
            if field not in scenario or not scenario[field]:
                issues.append(f"Missing required field: {field}")

        # Step count validation
        if 'steps' in scenario and len(scenario['steps']) != len(api_path):
            warnings.append(f"Step count mismatch: {len(scenario['steps'])} vs {len(api_path)}")

        # Scenario type specific validation
        scenario_type = scenario.get('scenario_type', 'normal')
        if scenario_type == 'exception':
            self._validate_exception_scenario(scenario, issues, warnings)
        elif scenario_type == 'normal':
            self._validate_normal_scenario(scenario, api_path, api_details, warnings)

        # Parameter binding validation
        if 'parameter_bindings' in scenario:
            self._validate_parameter_bindings(scenario['parameter_bindings'], api_path, warnings)

        # Path coverage check
        if api_details:
            self._validate_path_coverage(scenario, api_path, api_details, warnings)

        is_valid = len(issues) == 0

        return {
            'is_valid': is_valid,
            'issues': issues,
            'warnings': warnings,
            'score': self._calculate_score(scenario, issues, warnings)
        }

    def _validate_exception_scenario(self, scenario: Dict[str, Any],
                                     issues: List[str], warnings: List[str]):
        """Validate exception scenario has proper error injection."""
        if 'injection_point' not in scenario:
            issues.append("Exception scenario missing injection_point")
            return

        injection = scenario['injection_point']
        if 'expected_error' not in injection or not injection['expected_error']:
            warnings.append("Exception scenario should specify expected_error")

        # Check expected outcome mentions error
        outcome = scenario.get('expected_outcome', '').lower()
        if '成功' in outcome or 'success' in outcome:
            warnings.append("Exception scenario outcome should not indicate success")

    def _validate_normal_scenario(self, scenario: Dict[str, Any], api_path: List[str],
                                  api_details: Optional[Dict[str, Dict[str, Any]]],
                                  warnings: List[str]):
        """Validate normal scenario has proper flow."""
        # Check if path starts with login/auth
        if api_path and api_details:
            first_op = api_path[0]
            if first_op in api_details:
                first_detail = api_details[first_op]
                path = first_detail.get('path', '').lower()
                if 'login' in path or 'auth' in path:
                    desc = scenario.get('description', '').lower()
                    if '登录' not in desc and 'login' not in desc and '认证' not in desc:
                        warnings.append("Scenario starts with auth but description doesn't mention it")

    def _validate_parameter_bindings(self, bindings: Dict[str, Any],
                                     api_path: List[str], warnings: List[str]):
        """Validate parameter bindings use proper references."""
        for step, params in bindings.items():
            if step not in api_path:
                warnings.append(f"Parameter binding for unknown step: {step}")
                continue

            for param_name, param_config in params.items():
                if isinstance(param_config, dict):
                    param_type = param_config.get('type')
                    if param_type == 'dynamic_ref':
                        value = param_config.get('value', '')
                        if not value.startswith('{') or not value.endswith('}'):
                            warnings.append(f"Dynamic reference should use {{}} format: {param_name}")

    def _validate_path_coverage(self, scenario: Dict[str, Any], api_path: List[str],
                                api_details: Dict[str, Dict[str, Any]], warnings: List[str]):
        """Validate scenario covers write operations in path."""
        write_methods = {'POST', 'PUT', 'DELETE', 'PATCH'}
        write_ops = [op for op in api_path if op in api_details and
                     api_details[op].get('method') in write_methods]

        if write_ops:
            desc = scenario.get('description', '').lower()
            for op in write_ops:
                op_summary = api_details[op].get('summary', '').lower()
                # Simple check if write operation is mentioned
                if len(op_summary) > 3 and op_summary not in desc:
                    warnings.append(f"Write operation {op} not clearly described in scenario")
                    break  # Only warn once

    def _calculate_score(self, scenario: Dict[str, Any], issues: List[str], warnings: List[str]) -> float:
        """Calculate scenario quality score (0-1)."""
        if issues:
            return 0.0

        # Start with perfect score
        score = 1.0

        # Deduct for warnings
        score -= len(warnings) * 0.1

        # Bonus for detailed content
        if 'description' in scenario and len(scenario['description']) > 50:
            score += 0.1

        if 'steps' in scenario and len(scenario['steps']) > 2:
            score += 0.1

        return max(0.0, min(1.0, score))
