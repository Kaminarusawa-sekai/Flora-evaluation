"""Chaos engineering engine for mock server."""

from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass, field
import random
from fastapi.responses import JSONResponse


@dataclass
class ChaosRule:
    """Chaos injection rule."""
    api_pattern: str  # e.g., "/orders/*"
    method: Optional[str] = None
    trigger_count: Optional[int] = None  # Trigger on Nth call
    probability: float = 0.0  # 0-1
    action: Literal["fail_500", "fail_400", "latency", "stale_data", "token_expired"] = "fail_500"
    params: Dict[str, Any] = field(default_factory=dict)


class ChaosEngine:
    """Inject chaos into mock API responses."""

    def __init__(self, seed: Optional[int] = None):
        self.rules: Dict[str, ChaosRule] = {}
        self.call_counts: Dict[str, int] = {}
        self.stale_cache: Dict[str, Any] = {}  # For stale_data simulation
        if seed is not None:
            random.seed(seed)

    def add_rule(self, rule_id: str, rule: ChaosRule):
        """Add chaos injection rule."""
        self.rules[rule_id] = rule

    def should_inject(self, path: str, method: str) -> Optional[JSONResponse]:
        """Check if chaos should be injected."""
        key = f"{method}:{path}"
        self.call_counts[key] = self.call_counts.get(key, 0) + 1

        for rule in self.rules.values():
            if not self._match_pattern(path, rule.api_pattern):
                continue
            if rule.method and rule.method != method:
                continue

            # Count-based trigger
            if rule.trigger_count and self.call_counts[key] == rule.trigger_count:
                return self._execute_action(rule, key)

            # Probability-based trigger
            if rule.probability > 0 and random.random() < rule.probability:
                return self._execute_action(rule, key)

        return None

    def cache_stale_data(self, key: str, data: Any):
        """Cache data for stale_data simulation."""
        self.stale_cache[key] = data

    def get_stale_data(self, key: str) -> Optional[Any]:
        """Get cached stale data."""
        return self.stale_cache.get(key)

    def _match_pattern(self, path: str, pattern: str) -> bool:
        """Match path against pattern."""
        if pattern == "*":
            return True
        if pattern.endswith("/*"):
            return path.startswith(pattern[:-2])
        return path == pattern

    def _execute_action(self, rule: ChaosRule, key: str) -> Optional[JSONResponse]:
        """Execute chaos action."""
        if rule.action == "fail_500":
            return JSONResponse(status_code=500, content={"error": "Internal Server Error"})
        elif rule.action == "fail_400":
            return JSONResponse(status_code=400, content={"error": "Bad Request"})
        elif rule.action == "token_expired":
            return JSONResponse(status_code=401, content={"error": "Token expired"})
        elif rule.action == "stale_data":
            # Return marker to use stale data
            return None  # Handled in server
        return JSONResponse(status_code=503, content={"error": "Service Unavailable"})

    def reset_counts(self):
        """Reset call counters."""
        self.call_counts.clear()
        self.stale_cache.clear()
