"""Test entity-centric clustering to see the actual grouping."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_normalization import NormalizationService
import json

def main():
    print("=" * 80)
    print("Entity-Centric Clustering Test")
    print("=" * 80)

    # Initialize service with entity clustering
    service = NormalizationService(
        use_entity_clustering=True,
        entity_similarity_threshold=0.85,
        use_prance=True,
        enable_evaluation=False
    )

    # Parse Swagger
    print("\n[1] Parsing and clustering...")
    result = service.normalize_swagger('erp-server.json')

    # Group APIs by entity_anchor
    from collections import defaultdict
    entity_groups = defaultdict(list)

    # We need to access the clustered APIs directly
    parsed = service.parser.parse('erp-server.json')
    clustered_apis = service.clusterer.cluster(parsed['apis'])

    for api in clustered_apis:
        entity = api.get('entity_anchor', 'unknown')
        entity_groups[entity].append({
            'method': api['method'],
            'path': api.get('path', ''),
            'cluster': api.get('cluster', -1)
        })

    # Display entity groups
    print(f"\n[2] Found {len(entity_groups)} unique entities:\n")

    for entity, apis in sorted(entity_groups.items()):
        print(f"\n{'='*80}")
        print(f"Entity: {entity.upper()}")
        print(f"{'='*80}")
        print(f"Total APIs: {len(apis)}")

        # Group by cluster
        cluster_groups = defaultdict(list)
        for api in apis:
            cluster_groups[api['cluster']].append(api)

        print(f"Clusters: {len(cluster_groups)}")

        for cluster_id, cluster_apis in sorted(cluster_groups.items()):
            print(f"\n  Cluster {cluster_id} ({len(cluster_apis)} APIs):")
            for api in cluster_apis:
                print(f"    {api['method']:6} {api['path']}")

    print("\n" + "=" * 80)
    print(f"Summary: {len(entity_groups)} entities, {result['statistics']['total_capabilities']} capabilities")
    print("=" * 80)

if __name__ == '__main__':
    main()
