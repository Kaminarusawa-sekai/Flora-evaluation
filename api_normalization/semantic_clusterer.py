"""Semantic clustering of APIs based on vector similarity with hybrid strategy."""

from typing import List, Dict, Any, Tuple
import numpy as np
from collections import defaultdict
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticClusterer:
    """Cluster APIs based on semantic similarity using hybrid strategy."""

    def __init__(self,
                 min_cluster_size: int = 2,
                 min_samples: int = 2,
                 path_similarity_threshold: float = 0.8,
                 use_hdbscan: bool = True):
        """
        Initialize clusterer with hybrid strategy.

        Args:
            min_cluster_size: Minimum size for HDBSCAN clusters
            min_samples: Minimum samples for HDBSCAN
            path_similarity_threshold: Threshold for path-based clustering
            use_hdbscan: Whether to use HDBSCAN (falls back to DBSCAN if unavailable)
        """
        self.min_cluster_size = min_cluster_size
        self.min_samples = min_samples
        self.path_similarity_threshold = path_similarity_threshold
        self.use_hdbscan = use_hdbscan
        self.vectorizer = TfidfVectorizer(max_features=200, ngram_range=(1, 2))

    # Threshold: tag groups smaller than this are treated as a single cluster
    TAG_GROUP_SPLIT_THRESHOLD = 8

    def cluster(self, apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cluster APIs using hybrid strategy:
        Level 1 (Hard): Group by tags
        Level 2 (Soft): Semantic clustering within large tag groups
        Level 3: Path similarity refinement
        """
        if not apis:
            return []

        # Level 1: Pre-group by tags (hard rule)
        tag_groups = self._group_by_tags(apis)

        cluster_id = 0
        all_clustered_apis = []

        for tag, group_apis in tag_groups.items():
            if len(group_apis) == 1:
                # Single API in group - mark as atomic capability
                group_apis[0]['cluster'] = cluster_id
                group_apis[0]['cluster_type'] = 'atomic'
                all_clustered_apis.extend(group_apis)
                cluster_id += 1
                continue

            if len(group_apis) < self.TAG_GROUP_SPLIT_THRESHOLD:
                # Small tag group - keep as a single cluster (tag is strong signal)
                for api in group_apis:
                    api['cluster'] = cluster_id
                    api['cluster_type'] = 'tag_grouped'
                all_clustered_apis.extend(group_apis)
                cluster_id += 1
                continue

            # Level 2: Large tag group - semantic clustering to find sub-groups
            clustered_group = self._semantic_cluster(group_apis, cluster_id)

            # Level 3: Path similarity refinement
            clustered_group = self._refine_by_path_similarity(clustered_group)

            # Update cluster IDs
            max_label = max([api.get('cluster', -1) for api in clustered_group])
            cluster_id = max_label + 1 if max_label >= 0 else cluster_id

            all_clustered_apis.extend(clustered_group)

        # Handle noise points (cluster = -1)
        all_clustered_apis = self._handle_noise(all_clustered_apis)

        return all_clustered_apis

    def _group_by_tags(self, apis: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group APIs by their primary tag."""
        tag_groups = defaultdict(list)

        for api in apis:
            tags = api.get('tags', [])
            if tags:
                # Use first tag as primary
                primary_tag = tags[0]
            else:
                # No tag - use path prefix
                path_segments = api.get('path_segments', [])
                primary_tag = path_segments[0] if path_segments else 'untagged'

            tag_groups[primary_tag].append(api)

        return dict(tag_groups)

    def _semantic_cluster(self, apis: List[Dict[str, Any]], start_cluster_id: int) -> List[Dict[str, Any]]:
        """Perform semantic clustering using HDBSCAN or DBSCAN."""
        if len(apis) < 2:
            apis[0]['cluster'] = start_cluster_id
            return apis

        # Create enhanced text representations
        texts = [self._api_to_text(api) for api in apis]

        # Vectorize
        vectors = self.vectorizer.fit_transform(texts).toarray()

        # Try HDBSCAN first, fall back to DBSCAN
        labels = self._cluster_with_algorithm(vectors)

        # Adjust labels to start from start_cluster_id
        unique_labels = set(labels)
        label_mapping = {}
        next_id = start_cluster_id

        for label in sorted(unique_labels):
            if label == -1:
                label_mapping[-1] = -1  # Keep noise as -1
            else:
                label_mapping[label] = next_id
                next_id += 1

        # Assign cluster labels
        for api, label in zip(apis, labels):
            api['cluster'] = label_mapping[label]
            api['cluster_type'] = 'noise' if label == -1 else 'semantic'

        return apis

    def _cluster_with_algorithm(self, vectors: np.ndarray) -> np.ndarray:
        """Cluster using HDBSCAN or DBSCAN."""
        try:
            if self.use_hdbscan:
                import hdbscan
                clusterer = hdbscan.HDBSCAN(
                    min_cluster_size=self.min_cluster_size,
                    min_samples=self.min_samples,
                    metric='euclidean',
                    cluster_selection_method='eom'
                )
                labels = clusterer.fit_predict(vectors)
                return labels
        except ImportError:
            pass  # Fall back to DBSCAN

        # Fall back to DBSCAN
        from sklearn.cluster import DBSCAN

        # Dynamic eps calculation based on vector distribution
        eps = self._calculate_dynamic_eps(vectors)

        clustering = DBSCAN(eps=eps, min_samples=self.min_samples, metric='cosine')
        labels = clustering.fit_predict(vectors)
        return labels

    def _calculate_dynamic_eps(self, vectors: np.ndarray) -> float:
        """Calculate dynamic eps based on distance distribution."""
        if len(vectors) < 2:
            return 0.5

        # Calculate pairwise cosine distances
        similarities = cosine_similarity(vectors)
        distances = 1 - similarities

        # Use median distance as eps
        upper_triangle = distances[np.triu_indices_from(distances, k=1)]
        if len(upper_triangle) > 0:
            eps = np.median(upper_triangle)
            # Clamp between reasonable bounds
            return max(0.3, min(0.7, eps))

        return 0.5

    def _refine_by_path_similarity(self, apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Refine clusters by merging APIs with highly similar paths."""
        # Group by cluster
        clusters = defaultdict(list)
        for api in apis:
            cluster_id = api.get('cluster', -1)
            clusters[cluster_id].append(api)

        # Check path similarity within and across clusters
        for cluster_id, cluster_apis in clusters.items():
            if cluster_id == -1:
                continue

            for i, api1 in enumerate(cluster_apis):
                for api2 in cluster_apis[i+1:]:
                    if self._are_paths_similar(api1, api2):
                        # Ensure they're in the same cluster
                        if api1.get('cluster') != api2.get('cluster'):
                            # Merge to lower cluster ID
                            target_cluster = min(api1.get('cluster'), api2.get('cluster'))
                            api2['cluster'] = target_cluster

        return apis

    def _are_paths_similar(self, api1: Dict[str, Any], api2: Dict[str, Any]) -> bool:
        """Check if two APIs have similar paths."""
        path1_segments = api1.get('path_segments', [])
        path2_segments = api2.get('path_segments', [])

        if not path1_segments or not path2_segments:
            return False

        # Calculate segment overlap
        common_segments = set(path1_segments) & set(path2_segments)
        total_segments = set(path1_segments) | set(path2_segments)

        if not total_segments:
            return False

        similarity = len(common_segments) / len(total_segments)
        return similarity >= self.path_similarity_threshold

    def _handle_noise(self, apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Handle noise points by attempting to assign them to nearest cluster
        or marking as atomic capabilities.
        """
        noise_apis = [api for api in apis if api.get('cluster') == -1]
        clustered_apis = [api for api in apis if api.get('cluster') != -1]

        if not noise_apis or not clustered_apis:
            return apis

        # Create vectors for all APIs
        all_texts = [self._api_to_text(api) for api in apis]
        all_vectors = self.vectorizer.transform(all_texts).toarray()

        noise_indices = [i for i, api in enumerate(apis) if api.get('cluster') == -1]
        clustered_indices = [i for i, api in enumerate(apis) if api.get('cluster') != -1]

        # Calculate similarities
        for noise_idx in noise_indices:
            noise_vector = all_vectors[noise_idx].reshape(1, -1)

            max_similarity = -1
            best_cluster = -1

            for clustered_idx in clustered_indices:
                clustered_vector = all_vectors[clustered_idx].reshape(1, -1)
                similarity = cosine_similarity(noise_vector, clustered_vector)[0][0]

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_cluster = apis[clustered_idx].get('cluster')

            # If similarity is high enough, assign to cluster; otherwise mark as atomic
            if max_similarity >= 0.6:  # Threshold for noise recovery
                apis[noise_idx]['cluster'] = best_cluster
                apis[noise_idx]['cluster_type'] = 'recovered'
            else:
                # Assign unique cluster ID for atomic capability
                max_cluster_id = max([api.get('cluster', -1) for api in apis if api.get('cluster') != -1])
                apis[noise_idx]['cluster'] = max_cluster_id + 1 + noise_indices.index(noise_idx)
                apis[noise_idx]['cluster_type'] = 'atomic'

        return apis

    def _api_to_text(self, api: Dict[str, Any]) -> str:
        """
        Convert API to enhanced text representation for vectorization.
        Prioritizes action verbs and meaningful descriptions.
        """
        parts = []

        # Action verb (high weight - repeat 3 times)
        action_verb = api.get('action_verb', '')
        if action_verb:
            parts.extend([action_verb] * 3)

        # Summary and description
        summary = api.get('summary', '')
        description = api.get('description', '')

        if description and description != 'No description':
            parts.append(description)
        elif summary:
            parts.append(summary)
        else:
            # Fallback: use operation_id and path
            parts.append(api.get('operation_id', ''))
            parts.append(api.get('normalized_path', '').replace('/', ' '))

        # Tags
        tags = api.get('tags', [])
        if tags:
            parts.extend(tags)

        # Path segments (moderate weight)
        path_segments = api.get('path_segments', [])
        if path_segments:
            parts.extend(path_segments)

        # Method
        parts.append(api.get('method', ''))

        return ' '.join(filter(None, parts))
