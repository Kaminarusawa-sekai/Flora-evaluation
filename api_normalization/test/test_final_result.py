"""Test final entity-centric clustering result."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_normalization import NormalizationService
import json

def main():
    print("=" * 80)
    print("Entity-Centric Clustering - Final Result")
    print("=" * 80)

    # Initialize service with entity clustering
    service = NormalizationService(
        use_entity_clustering=True,
        entity_similarity_threshold=0.85,
        use_prance=True,
        enable_evaluation=True
    )

    # Parse and normalize
    print("\n[1] Parsing and clustering...")
    result = service.normalize_swagger('erp-server.json')

    # Display statistics
    print("\n[2] Statistics:")
    stats = result['statistics']
    print(f"  Total APIs: {stats['total_apis']}")
    print(f"  Total Capabilities: {stats['total_capabilities']}")
    print(f"  - Composite Capabilities: {stats['semantic_capabilities']}")
    print(f"  - Atomic Capabilities: {stats['atomic_capabilities']}")

    # Display capabilities with CRUD completeness
    print("\n[3] Capabilities (showing complete CRUD capabilities):")

    complete_crud = []
    incomplete_crud = []

    for cap in result['capabilities']:
        if cap.get('lifecycle', {}).get('is_complete_crud'):
            complete_crud.append(cap)
        else:
            incomplete_crud.append(cap)

    print(f"\n  Complete CRUD Capabilities ({len(complete_crud)}):")
    print("  " + "=" * 76)

    for i, cap in enumerate(complete_crud, 1):
        print(f"\n  [{i}] {cap['name']}")
        print(f"      Resource: {cap.get('resource', 'N/A')}")
        print(f"      APIs: {cap['api_count']}")

        # Show CRUD operations
        crud_ops = []
        lc = cap.get('lifecycle', {})
        if lc.get('has_create'): crud_ops.append('Create')
        if lc.get('has_read'): crud_ops.append('Read')
        if lc.get('has_update'): crud_ops.append('Update')
        if lc.get('has_delete'): crud_ops.append('Delete')
        print(f"      CRUD: {', '.join(crud_ops)}")

        # Show API list
        print(f"      Operations:")
        for api in cap['apis']:
            method = api['method']
            path = api.get('path', '')
            # Extract last segment
            last_segment = path.split('/')[-1] if '/' in path else path
            print(f"        {method:6} .../{last_segment}")

    print(f"\n  Incomplete CRUD Capabilities ({len(incomplete_crud)}):")
    print("  " + "=" * 76)

    for i, cap in enumerate(incomplete_crud[:5], 1):  # Show first 5
        print(f"\n  [{i}] {cap['name']}")
        print(f"      Resource: {cap.get('resource', 'N/A')}")
        print(f"      APIs: {cap['api_count']}")

        # Show CRUD operations
        crud_ops = []
        lc = cap.get('lifecycle', {})
        if lc.get('has_create'): crud_ops.append('Create')
        if lc.get('has_read'): crud_ops.append('Read')
        if lc.get('has_update'): crud_ops.append('Update')
        if lc.get('has_delete'): crud_ops.append('Delete')
        print(f"      CRUD: {', '.join(crud_ops)}")

    if len(incomplete_crud) > 5:
        print(f"\n  ... and {len(incomplete_crud) - 5} more")

    # Display evaluation
    if result.get('evaluation'):
        ev = result['evaluation']
        print(f"\n[4] Clustering Quality:")
        print(f"  Overall Score: {ev['quality_score']:.2f}/100")

        metrics = ev.get('metrics', {})
        print(f"  Silhouette Score: {metrics.get('silhouette_score', 0):.4f}")
        print(f"  Davies-Bouldin Index: {metrics.get('davies_bouldin_index', 0):.4f}")
        print(f"  Avg Cluster Size: {metrics.get('avg_cluster_size', 0):.1f}")

    print("\n" + "=" * 80)
    print("Entity-centric clustering completed successfully!")
    print("=" * 80)

if __name__ == '__main__':
    main()
