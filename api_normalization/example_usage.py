"""
API Normalization Service - Complete Example

This example demonstrates all features of the API normalization service.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_normalization import NormalizationService, ClusterEvaluator
import json


def main():
    print("=" * 70)
    print("API Normalization Service - Complete Example")
    print("=" * 70)

    # Initialize service with all features enabled
    service = NormalizationService(
        min_cluster_size=2,
        min_samples=2,
        path_similarity_threshold=0.8,
        use_hdbscan=True,
        use_prance=True,
        enable_evaluation=True
    )

    # Parse Swagger document
    print("\n[1] Parsing Swagger document...")
    result = service.normalize_swagger('example_swagger.json')

    # Display statistics
    print("\n[2] Statistics:")
    stats = result['statistics']
    print(f"  Total APIs: {stats['total_apis']}")
    print(f"  Total Capabilities: {stats['total_capabilities']}")
    print(f"  - Semantic Capabilities: {stats['semantic_capabilities']}")
    print(f"  - Atomic Capabilities: {stats['atomic_capabilities']}")

    # Display capabilities
    print("\n[3] Extracted Capabilities:")
    for i, cap in enumerate(result['capabilities'], 1):
        print(f"\n  [{i}] {cap['name']}")
        print(f"      Type: {cap['type']}")
        print(f"      APIs: {cap['api_count']}")

        if cap.get('resource'):
            print(f"      Resource: {cap['resource']}")

        if cap.get('primary_action'):
            print(f"      Primary Action: {cap['primary_action']}")

        # Lifecycle
        lc = cap.get('lifecycle', {})
        if lc:
            crud_ops = []
            if lc.get('has_create'): crud_ops.append('Create')
            if lc.get('has_read'): crud_ops.append('Read')
            if lc.get('has_update'): crud_ops.append('Update')
            if lc.get('has_delete'): crud_ops.append('Delete')
            print(f"      CRUD: {', '.join(crud_ops)}")
            print(f"      Complete CRUD: {'Yes' if lc.get('is_complete_crud') else 'No'}")

        # Connectivity
        if cap.get('connectivity_score') is not None:
            score = cap['connectivity_score']
            print(f"      Connectivity Score: {score:.2f}")

        # Workflow
        if cap.get('typical_workflow'):
            print(f"      Workflow: {cap['typical_workflow']}")

        # Schema
        schema = cap.get('unified_schema', {})
        if schema.get('properties'):
            props = list(schema['properties'].keys())
            print(f"      Schema Fields: {', '.join(props)}")
            if schema.get('required'):
                print(f"      Required: {', '.join(schema['required'])}")
            if schema.get('read_only'):
                print(f"      Read-only: {', '.join(schema['read_only'])}")
            if schema.get('write_only'):
                print(f"      Write-only: {', '.join(schema['write_only'])}")

        # List APIs
        print(f"      APIs:")
        for api in cap['apis']:
            method = api['method']
            path = api.get('normalized_path', api['path'])
            summary = api.get('summary', '')
            print(f"        - {method:6} {path}")
            if summary:
                print(f"          {summary}")

    # Display evaluation
    if result.get('evaluation'):
        ev = result['evaluation']
        print(f"\n[4] Clustering Quality Evaluation:")
        print(f"  Overall Quality Score: {ev['quality_score']:.2f}/100")

        metrics = ev.get('metrics', {})
        print(f"\n  Metrics:")
        print(f"    - Silhouette Score: {metrics.get('silhouette_score', 0):.4f}")
        print(f"    - Davies-Bouldin Index: {metrics.get('davies_bouldin_index', 0):.4f}")
        print(f"    - Total Clusters: {metrics.get('total_clusters', 0)}")
        print(f"    - Noise Ratio: {metrics.get('noise_ratio', 0):.1%}")
        print(f"    - Avg Cluster Size: {metrics.get('avg_cluster_size', 0):.1f}")

        # Connectivity scores
        conn_scores = ev.get('connectivity_scores', {})
        if conn_scores.get('per_capability'):
            print(f"\n  Connectivity Scores:")
            for cap_score in conn_scores['per_capability']:
                print(f"    - {cap_score['capability_name']}: {cap_score['connectivity_score']:.2f}")

        # Warnings
        if ev.get('warnings'):
            print(f"\n  Warnings:")
            for warning in ev['warnings']:
                print(f"    ! {warning}")

        # Recommendations
        if ev.get('recommendations'):
            print(f"\n  Recommendations:")
            for rec in ev['recommendations']:
                print(f"    * {rec}")

        # Explanations
        if ev.get('explanations'):
            print(f"\n  Capability Explanations:")
            for exp in ev['explanations']:
                print(f"\n    {exp['capability_name']}:")
                print(f"      Reason: {exp['reason']}")
                if exp.get('key_features'):
                    print(f"      Key Features: {', '.join(exp['key_features'])}")

    # Generate capability cards
    print("\n[5] Capability Cards:")
    evaluator = ClusterEvaluator()
    for cap in result['capabilities'][:2]:  # Show first 2
        print("\n" + "─" * 70)
        card = evaluator.generate_capability_card(cap)
        print(card)

    # Export results
    print("\n[6] Exporting results...")
    output_path = 'api_normalization/output/example_result.json'
    service.normalize_and_export('example_swagger.json', output_path)
    print(f"  Results exported to: {output_path}")

    print("\n" + "=" * 70)
    print("Example completed successfully!")
    print("=" * 70)


if __name__ == '__main__':
    main()
