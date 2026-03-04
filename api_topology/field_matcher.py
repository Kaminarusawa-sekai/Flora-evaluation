"""Field matching with multi-factor scoring."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
import Levenshtein
from .semantic_matcher import SemanticMatcher
from .entity_canonicalizer import EntityCanonicalizer
from .path_extractor import PathExtractor


@dataclass
class FieldMatch:
    """Field matching result."""
    source_field: str
    target_field: str
    score: float
    match_type: str  # 'CERTAIN', 'PROBABLE', 'WEAK'
    source_path: str  # JSON path like 'user.id'
    target_path: str
    entity: Optional[str] = None  # Canonical entity if matched


class FieldMatcher:
    """Match fields between API responses and requests."""

    # Common noise fields to exclude
    NOISE_FIELDS = {'timestamp', 'message', 'code', 'status', 'msg', 'success', 'error'}

    # Parameter location weights
    LOCATION_WEIGHTS = {
        'path': 0.95,
        'query': 0.70,
        'body': 0.50
    }

    def __init__(self, name_threshold: float = 0.5, final_threshold: float = 0.7,
                 llm_client=None, use_semantic: bool = True):
        self.name_threshold = name_threshold
        self.final_threshold = final_threshold

        # Initialize advanced matchers
        self.semantic = SemanticMatcher() if use_semantic else None
        self.canonicalizer = EntityCanonicalizer(llm_client)
        self.path_extractor = PathExtractor()

    def calculate_score(self,
                       source_field: Dict[str, Any],
                       target_field: Dict[str, Any],
                       same_cluster: bool = False,
                       api_context_source: str = "",
                       api_context_target: str = "") -> float:
        """Calculate matching score between two fields."""

        # Skip noise fields
        if (source_field['name'] in self.NOISE_FIELDS or
            target_field['name'] in self.NOISE_FIELDS):
            return 0.0

        # Type must match
        if source_field.get('type') != target_field.get('type'):
            return 0.0

        score = 0.0

        # 1. Entity matching (highest priority - 40% weight)
        if self.canonicalizer.fields_match_by_entity(
            source_field, target_field, api_context_source, api_context_target
        ):
            score += 0.4

        # 2. Name similarity (30% weight)
        name_sim = self._name_similarity(source_field['name'], target_field['name'])
        if name_sim < self.name_threshold:
            return score  # Continue if entity matched
        score += 0.3 * name_sim

        # 3. Semantic similarity (15% weight)
        if self.semantic and self.semantic.is_available():
            desc1 = source_field.get('description', source_field['name'])
            desc2 = target_field.get('description', target_field['name'])
            sem_sim = self.semantic.calculate_similarity(desc1, desc2)
            score += 0.15 * sem_sim

        # 4. Location weight (10% weight)
        source_loc = source_field.get('location', 'body')
        target_loc = target_field.get('location', 'body')
        loc_weight = min(self.LOCATION_WEIGHTS.get(source_loc, 0.5),
                        self.LOCATION_WEIGHTS.get(target_loc, 0.5))
        score += 0.1 * loc_weight

        # 5. Cluster bonus (5% weight)
        if same_cluster:
            score += 0.05

        return min(score, 1.0)

    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate name similarity using Levenshtein distance."""
        name1 = name1.lower().replace('_', '').replace('-', '')
        name2 = name2.lower().replace('_', '').replace('-', '')

        if name1 == name2:
            return 1.0

        distance = Levenshtein.distance(name1, name2)
        max_len = max(len(name1), len(name2))
        return 1.0 - (distance / max_len) if max_len > 0 else 0.0

    def classify_match(self, score: float) -> Optional[str]:
        """Classify match confidence level."""
        if score >= 0.9:
            return 'CERTAIN'
        elif score >= self.final_threshold:
            return 'PROBABLE'
        elif score >= 0.5:
            return 'WEAK'
        return None
