"""Evaluation and explainability module for clustering quality."""

from typing import List, Dict, Any, Tuple
import numpy as np
from collections import defaultdict
from sklearn.metrics import silhouette_score, davies_bouldin_score
from sklearn.feature_extraction.text import TfidfVectorizer


class ClusterEvaluator:
    """Evaluate clustering quality and provide explainability."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=200, ngram_range=(1, 2))

    def evaluate(self, apis: List[Dict[str, Any]], capabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Evaluate clustering quality and generate explanations.

        Args:
            apis: List of clustered APIs
            capabilities: List of extracted capabilities

        Returns:
            Evaluation metrics and explanations
        """
        if not apis or len(apis) < 2:
            return {
                'quality_score': 0.0,
                'metrics': {},
                'explanations': [],
                'warnings': ['Insufficient data for evaluation']
            }

        # Calculate clustering metrics
        metrics = self._calculate_metrics(apis)

        # Generate per-capability explanations
        explanations = self._generate_explanations(capabilities)

        # Calculate connectivity scores
        connectivity_scores = self._evaluate_connectivity(capabilities)

        # Detect potential issues
        warnings = self._detect_issues(apis, capabilities, metrics)

        # Overall quality score (0-100)
        quality_score = self._calculate_quality_score(metrics, connectivity_scores)

        return {
            'quality_score': quality_score,
            'metrics': metrics,
            'connectivity_scores': connectivity_scores,
            'explanations': explanations,
            'warnings': warnings,
            'recommendations': self._generate_recommendations(metrics, warnings)
        }

    def _calculate_metrics(self, apis: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate clustering quality metrics."""
        # Prepare data
        texts = [self._api_to_text(api) for api in apis]
        vectors = self.vectorizer.fit_transform(texts).toarray()
        labels = np.array([api.get('cluster', -1) for api in apis])

        # Filter out noise points for some metrics
        non_noise_mask = labels != -1
        non_noise_vectors = vectors[non_noise_mask]
        non_noise_labels = labels[non_noise_mask]

        metrics = {}

        # Silhouette Score (higher is better, range: -1 to 1)
        if len(set(non_noise_labels)) > 1 and len(non_noise_labels) > 1:
            try:
                metrics['silhouette_score'] = float(silhouette_score(non_noise_vectors, non_noise_labels))
            except:
                metrics['silhouette_score'] = 0.0
        else:
            metrics['silhouette_score'] = 0.0

        # Davies-Bouldin Index (lower is better)
        if len(set(non_noise_labels)) > 1:
            try:
                metrics['davies_bouldin_index'] = float(davies_bouldin_score(non_noise_vectors, non_noise_labels))
            except:
                metrics['davies_bouldin_index'] = 0.0
        else:
            metrics['davies_bouldin_index'] = 0.0

        # Cluster distribution metrics
        cluster_counts = defaultdict(int)
        for label in labels:
            cluster_counts[label] += 1

        total_clusters = len([k for k in cluster_counts.keys() if k != -1])
        noise_count = cluster_counts.get(-1, 0)
        noise_ratio = noise_count / len(apis) if apis else 0

        metrics['total_clusters'] = total_clusters
        metrics['noise_ratio'] = noise_ratio
        metrics['avg_cluster_size'] = np.mean([v for k, v in cluster_counts.items() if k != -1]) if total_clusters > 0 else 0
        metrics['cluster_size_std'] = np.std([v for k, v in cluster_counts.items() if k != -1]) if total_clusters > 0 else 0

        return metrics

    def _evaluate_connectivity(self, capabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate API connectivity within capabilities."""
        scores = []

        for cap in capabilities:
            score = cap.get('connectivity_score', 0.0)
            scores.append({
                'capability_id': cap['id'],
                'capability_name': cap['name'],
                'connectivity_score': score
            })

        avg_score = np.mean([s['connectivity_score'] for s in scores]) if scores else 0.0

        return {
            'average_connectivity': avg_score,
            'per_capability': scores
        }

    def _generate_explanations(self, capabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate human-readable explanations for each capability."""
        explanations = []

        for cap in capabilities:
            explanation = {
                'capability_id': cap['id'],
                'capability_name': cap['name'],
                'type': cap.get('type', 'composite'),
                'reason': self._explain_capability(cap),
                'typical_workflow': cap.get('typical_workflow', ''),
                'key_features': self._extract_key_features(cap)
            }
            explanations.append(explanation)

        return explanations

    def _explain_capability(self, cap: Dict[str, Any]) -> str:
        """Generate explanation for why APIs are grouped together."""
        cap_type = cap.get('type', 'composite')

        if cap_type == 'atomic':
            return f"Atomic capability - single independent API operation: {cap.get('description', 'No description')}"

        apis = cap.get('apis', [])
        resource = cap.get('resource', 'unknown')
        lifecycle = cap.get('lifecycle', {})

        reasons = []

        # Resource-based reason
        if resource and resource != 'unknown':
            reasons.append(f"All APIs operate on the '{resource}' resource")

        # Lifecycle-based reason
        lifecycle_ops = []
        if lifecycle.get('has_create'):
            lifecycle_ops.append('create')
        if lifecycle.get('has_read'):
            lifecycle_ops.append('read')
        if lifecycle.get('has_update'):
            lifecycle_ops.append('update')
        if lifecycle.get('has_delete'):
            lifecycle_ops.append('delete')

        if lifecycle_ops:
            reasons.append(f"Covers {', '.join(lifecycle_ops)} operations")

        # Path similarity reason
        paths = [api.get('normalized_path', '') for api in apis]
        if paths and len(set(paths)) < len(paths):
            reasons.append("APIs share similar URL patterns")

        # Tag-based reason
        tags = cap.get('tags', [])
        if tags:
            reasons.append(f"Tagged as: {', '.join(tags[:3])}")

        if not reasons:
            reasons.append("APIs grouped by semantic similarity")

        return ". ".join(reasons) + "."

    def _extract_key_features(self, cap: Dict[str, Any]) -> List[str]:
        """Extract key features of a capability."""
        features = []

        # API count
        api_count = cap.get('api_count', 0)
        features.append(f"{api_count} API{'s' if api_count != 1 else ''}")

        # HTTP methods
        methods = set(api['method'] for api in cap.get('apis', []))
        if methods:
            features.append(f"Methods: {', '.join(sorted(methods))}")

        # Lifecycle completeness
        lifecycle = cap.get('lifecycle', {})
        completeness = lifecycle.get('completeness', 0)
        if completeness > 0:
            features.append(f"Lifecycle: {int(completeness * 100)}% complete")

        # Connectivity
        connectivity = cap.get('connectivity_score', 0)
        if connectivity > 0.7:
            features.append("High connectivity")
        elif connectivity > 0.4:
            features.append("Medium connectivity")

        return features

    def _detect_issues(self, apis: List[Dict[str, Any]],
                      capabilities: List[Dict[str, Any]],
                      metrics: Dict[str, float]) -> List[str]:
        """Detect potential issues in clustering."""
        warnings = []

        # High noise ratio
        noise_ratio = metrics.get('noise_ratio', 0)
        if noise_ratio > 0.3:
            warnings.append(f"High noise ratio ({noise_ratio:.1%}): Many APIs couldn't be clustered. Consider adjusting clustering parameters.")

        # Low silhouette score
        silhouette = metrics.get('silhouette_score', 0)
        if silhouette < 0.2:
            warnings.append(f"Low silhouette score ({silhouette:.2f}): Clusters may not be well-separated. Review clustering quality.")

        # Very large clusters
        for cap in capabilities:
            if cap.get('api_count', 0) > 20:
                warnings.append(f"Large cluster '{cap['name']}' ({cap['api_count']} APIs): Consider splitting into sub-capabilities.")

        # Incomplete lifecycles
        incomplete_caps = [cap for cap in capabilities
                          if cap.get('type') == 'composite' and cap.get('lifecycle', {}).get('completeness', 0) < 0.5]
        if len(incomplete_caps) > len(capabilities) * 0.5:
            warnings.append(f"{len(incomplete_caps)} capabilities have incomplete CRUD operations. This may indicate missing APIs or over-clustering.")

        # Low connectivity
        low_connectivity_caps = [cap for cap in capabilities
                                if cap.get('connectivity_score', 0) < 0.3]
        if low_connectivity_caps:
            warnings.append(f"{len(low_connectivity_caps)} capabilities have low connectivity scores. APIs may not form coherent workflows.")

        return warnings

    def _calculate_quality_score(self, metrics: Dict[str, float],
                                 connectivity_scores: Dict[str, Any]) -> float:
        """Calculate overall quality score (0-100)."""
        score = 0.0
        weights = {
            'silhouette': 0.3,
            'noise': 0.2,
            'connectivity': 0.3,
            'distribution': 0.2
        }

        # Silhouette score component (normalize from [-1, 1] to [0, 1])
        silhouette = metrics.get('silhouette_score', 0)
        silhouette_normalized = (silhouette + 1) / 2
        score += silhouette_normalized * weights['silhouette']

        # Noise ratio component (invert - lower is better)
        noise_ratio = metrics.get('noise_ratio', 0)
        noise_score = max(0, 1 - noise_ratio * 2)  # Penalize heavily above 50%
        score += noise_score * weights['noise']

        # Connectivity component
        avg_connectivity = connectivity_scores.get('average_connectivity', 0)
        score += avg_connectivity * weights['connectivity']

        # Distribution component (prefer moderate cluster sizes)
        avg_size = metrics.get('avg_cluster_size', 0)
        size_std = metrics.get('cluster_size_std', 0)
        if avg_size > 0:
            # Ideal cluster size is 3-8 APIs
            size_score = 1.0 if 3 <= avg_size <= 8 else max(0, 1 - abs(avg_size - 5.5) / 10)
            # Penalize high variance
            variance_penalty = min(1.0, size_std / avg_size) if avg_size > 0 else 0
            distribution_score = size_score * (1 - variance_penalty * 0.5)
        else:
            distribution_score = 0.0

        score += distribution_score * weights['distribution']

        return round(score * 100, 2)

    def _generate_recommendations(self, metrics: Dict[str, float],
                                  warnings: List[str]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        silhouette = metrics.get('silhouette_score', 0)
        noise_ratio = metrics.get('noise_ratio', 0)
        avg_size = metrics.get('avg_cluster_size', 0)

        if silhouette < 0.2:
            recommendations.append("Consider using more descriptive API documentation (summary, description) to improve semantic clustering.")

        if noise_ratio > 0.3:
            recommendations.append("High noise ratio detected. Try: 1) Lowering min_cluster_size, 2) Improving API descriptions, 3) Adding more tags to APIs.")

        if avg_size > 10:
            recommendations.append("Large average cluster size. Consider: 1) Using stricter clustering parameters, 2) Adding more granular tags.")

        if avg_size < 2:
            recommendations.append("Very small clusters. Consider: 1) Relaxing clustering parameters, 2) Checking if APIs are too diverse.")

        if not recommendations:
            recommendations.append("Clustering quality looks good! Continue monitoring as you add more APIs.")

        return recommendations

    def _api_to_text(self, api: Dict[str, Any]) -> str:
        """Convert API to text representation."""
        action_verb = api.get('action_verb', '')
        summary = api.get('summary', '')
        description = api.get('description', '')
        tags = ' '.join(api.get('tags', []))
        path_segments = ' '.join(api.get('path_segments', []))
        method = api.get('method', '')

        parts = [
            f"{action_verb} {action_verb}" if action_verb else '',  # Double weight for action verbs
            summary,
            description,
            tags,
            path_segments,
            method
        ]

        return ' '.join(filter(None, parts))

    def generate_capability_card(self, capability: Dict[str, Any]) -> str:
        """
        Generate a human-readable capability card for agents.

        Returns:
            Formatted capability description
        """
        lines = []
        lines.append(f"# Capability: {capability['name']}")
        lines.append(f"Type: {capability.get('type', 'composite').title()}")
        lines.append("")

        # Description
        description = capability.get('description', '')
        if description:
            lines.append(f"## Description")
            lines.append(description)
            lines.append("")

        # Resource
        resource = capability.get('resource', '')
        if resource and resource != 'unknown':
            lines.append(f"## Resource")
            lines.append(f"Operates on: {resource}")
            lines.append("")

        # APIs
        lines.append(f"## APIs ({capability.get('api_count', 0)})")
        for api in capability.get('apis', []):
            action = api.get('action_verb', '')
            action_str = f"[{action}] " if action else ""
            lines.append(f"- {action_str}{api['method']} {api['path']}")
            if api.get('summary'):
                lines.append(f"  {api['summary']}")
        lines.append("")

        # Typical workflow
        workflow = capability.get('typical_workflow', '')
        if workflow:
            lines.append(f"## Typical Workflow")
            lines.append(workflow)
            lines.append("")

        # Schema
        schema = capability.get('unified_schema', {})
        if schema.get('properties'):
            lines.append(f"## Key Fields")
            for prop, prop_schema in list(schema['properties'].items())[:5]:  # Top 5
                prop_type = prop_schema.get('type', 'unknown')
                required = " (required)" if prop in schema.get('required', []) else ""
                read_only = " [read-only]" if prop in schema.get('read_only', []) else ""
                write_only = " [write-only]" if prop in schema.get('write_only', []) else ""
                lines.append(f"- {prop}: {prop_type}{required}{read_only}{write_only}")
            lines.append("")

        # Connectivity
        connectivity = capability.get('connectivity_score', 0)
        if connectivity > 0:
            lines.append(f"## Connectivity Score: {connectivity:.2f}")
            if connectivity > 0.7:
                lines.append("High connectivity - APIs form a complete workflow")
            elif connectivity > 0.4:
                lines.append("Medium connectivity - Some workflow gaps may exist")
            else:
                lines.append("Low connectivity - APIs may be loosely related")
            lines.append("")

        return '\n'.join(lines)
