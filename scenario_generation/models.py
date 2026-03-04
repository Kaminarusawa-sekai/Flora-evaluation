"""Data models for scenario generation."""

from typing import Dict, Any, List, Optional, Literal
from dataclasses import dataclass, field


@dataclass
class ParameterConstraint:
    """Parameter constraint for dynamic binding."""
    type: Literal["static", "dynamic_ref", "fake_data"]
    value: Optional[str] = None  # For static or reference expression
    rule: Optional[str] = None  # For dynamic constraints like "must_have_unpaid_order"


@dataclass
class InjectionPoint:
    """Error injection point for exception scenarios."""
    step_index: int
    injection_type: Literal["missing_link", "state_conflict", "permission_gap", "invalid_data"]
    description: str
    expected_error: str  # Expected error code or message


@dataclass
class TestScenario:
    """Enhanced test scenario with dynamic references."""
    title: str
    description: str
    scenario_type: Literal["normal", "exception", "boundary", "info_missing", "logic_nested", "conflict_prevention"]
    steps: List[str]
    parameter_bindings: Dict[str, ParameterConstraint]
    expected_outcome: str
    injection_point: Optional[InjectionPoint] = None
    dependency_map: Dict[str, str] = field(default_factory=dict)  # step_name -> depends_on
