"""Main service interface for API normalization."""

from typing import Dict, Any, Optional
from .swagger_parser import SwaggerParser
from .semantic_clusterer import SemanticClusterer
from .entity_clusterer import EntityClusterer
from .capability_extractor import CapabilityExtractor
from .evaluator import ClusterEvaluator


class NormalizationService:
    """Service for normalizing Swagger APIs into capability models."""

    def __init__(self,
                 min_cluster_size: int = 2,
                 min_samples: int = 2,
                 path_similarity_threshold: float = 0.8,
                 use_hdbscan: bool = True,
                 use_prance: bool = True,
                 enable_evaluation: bool = True,
                 use_entity_clustering: bool = True,
                 entity_similarity_threshold: float = 0.85):
        """
        Initialize normalization service.

        Args:
            min_cluster_size: Minimum cluster size for HDBSCAN
            min_samples: Minimum samples for clustering
            path_similarity_threshold: Threshold for path-based clustering
            use_hdbscan: Whether to use HDBSCAN (falls back to DBSCAN)
            use_prance: Whether to use prance for enhanced parsing
            enable_evaluation: Whether to evaluate clustering quality
            use_entity_clustering: Whether to use entity-centric clustering (recommended)
            entity_similarity_threshold: Similarity threshold for entity clustering (0.85 default)
        """
        self.parser = SwaggerParser(use_prance=use_prance)
        self.use_entity_clustering = use_entity_clustering

        if use_entity_clustering:
            self.clusterer = EntityClusterer(
                similarity_threshold=entity_similarity_threshold
            )
        else:
            self.clusterer = SemanticClusterer(
                min_cluster_size=min_cluster_size,
                min_samples=min_samples,
                path_similarity_threshold=path_similarity_threshold,
                use_hdbscan=use_hdbscan
            )

        self.extractor = CapabilityExtractor()
        self.evaluator = ClusterEvaluator() if enable_evaluation else None
        self.enable_evaluation = enable_evaluation

    def normalize_swagger(self, source: str) -> Dict[str, Any]:
        """
        Parse Swagger file/URL and extract normalized capabilities.

        Args:
            source: Path to Swagger/OpenAPI file or URL (.json, .yaml, .yml)

        Returns:
            Dict containing capabilities, metadata, and evaluation results
        """
        # Parse Swagger
        parsed = self.parser.parse(source)

        # Cluster APIs
        clustered_apis = self.clusterer.cluster(parsed['apis'])

        # Extract capabilities
        capabilities_result = self.extractor.extract(clustered_apis)

        # Evaluate clustering quality
        evaluation = None
        if self.enable_evaluation and self.evaluator:
            evaluation = self.evaluator.evaluate(
                clustered_apis,
                capabilities_result['capabilities']
            )

        # Build result
        result = {
            'capabilities': capabilities_result['capabilities'],
            'statistics': {
                'total_apis': capabilities_result['total_apis'],
                'total_capabilities': capabilities_result['total_capabilities'],
                'semantic_capabilities': capabilities_result.get('semantic_capabilities', 0),
                'atomic_capabilities': capabilities_result.get('atomic_capabilities', 0)
            },
            'source': {
                'title': parsed['title'],
                'version': parsed['version'],
                'source': source
            }
        }

        if evaluation:
            result['evaluation'] = evaluation

        return result

    def normalize_and_export(self, source: str, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Normalize Swagger and optionally export to file.

        Args:
            source: Path to Swagger/OpenAPI file or URL
            output_path: Optional path to export normalized result

        Returns:
            Normalized capabilities with evaluation
        """
        result = self.normalize_swagger(source)

        if output_path:
            import json
            from pathlib import Path

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        return result

    def get_capability_card(self, capability: Dict[str, Any]) -> str:
        """
        Generate a human-readable capability card.

        Args:
            capability: Capability dictionary

        Returns:
            Formatted capability card as string
        """
        lines = []
        lines.append(f"╔══════════════════════════════════════════════════════════════╗")
        lines.append(f"║  Capability: {capability['name']:<46} ║")
        lines.append(f"╠══════════════════════════════════════════════════════════════╣")
        lines.append(f"║  ID: {capability['id']:<54} ║")
        lines.append(f"║  Type: {capability.get('type', 'composite'):<52} ║")

        if capability.get('resource'):
            lines.append(f"║  Resource: {capability['resource']:<48} ║")

        if capability.get('primary_action'):
            lines.append(f"║  Primary Action: {capability['primary_action']:<42} ║")

        lines.append(f"║  API Count: {capability['api_count']:<47} ║")

        if capability.get('connectivity_score') is not None:
            score = capability['connectivity_score']
            score_str = f"{score:.2f}"
            lines.append(f"║  Connectivity Score: {score_str:<38} ║")

        lines.append(f"╠══════════════════════════════════════════════════════════════╣")
        lines.append(f"║  Description:                                                ║")

        desc = capability.get('description', 'No description')
        # Wrap description
        max_width = 58
        words = desc.split()
        current_line = ""
        for word in words:
            if len(current_line) + len(word) + 1 <= max_width:
                current_line += (" " if current_line else "") + word
            else:
                lines.append(f"║  {current_line:<58} ║")
                current_line = word
        if current_line:
            lines.append(f"║  {current_line:<58} ║")

        if capability.get('typical_workflow'):
            lines.append(f"╠══════════════════════════════════════════════════════════════╣")
            lines.append(f"║  Typical Workflow:                                           ║")
            workflow = capability['typical_workflow']
            lines.append(f"║  {workflow:<58} ║")

        lines.append(f"╠══════════════════════════════════════════════════════════════╣")
        lines.append(f"║  APIs:                                                       ║")

        for api in capability.get('apis', [])[:5]:  # Show first 5 APIs
            method = api['method']
            path = api.get('normalized_path', api['path'])
            api_line = f"{method} {path}"
            if len(api_line) > 56:
                api_line = api_line[:53] + "..."
            lines.append(f"║    {api_line:<56} ║")

        if len(capability.get('apis', [])) > 5:
            remaining = len(capability['apis']) - 5
            lines.append(f"║    ... and {remaining} more APIs{'':<{56-len(f'... and {remaining} more APIs')}} ║")

        lines.append(f"╚══════════════════════════════════════════════════════════════╝")

        return "\n".join(lines)
