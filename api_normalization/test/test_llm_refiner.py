"""Test LLM cluster refiner on scattered APIs."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_normalization import NormalizationService
from api_normalization.llm_cluster_refiner import LLMClusterRefiner
from collections import defaultdict
import json


def main():
    print("=" * 80)
    print("LLM Cluster Refiner Test")
    print("=" * 80)

    # Step 1: Initial clustering
    print("\n[1] Initial clustering with entity-centric approach...")
    service = NormalizationService(
        use_entity_clustering=True,
        entity_similarity_threshold=0.85,
        use_prance=True,
        enable_evaluation=False
    )

    parsed = service.parser.parse('erp-server.json')
    clustered_apis = service.clusterer.cluster(parsed['apis'])

    # Show initial statistics
    cluster_sizes = defaultdict(int)
    for api in clustered_apis:
        cluster_sizes[api['cluster']] += 1

    scattered_count = sum(1 for size in cluster_sizes.values() if size < 3)
    print(f"\nInitial clustering:")
    print(f"  Total APIs: {len(clustered_apis)}")
    print(f"  Total clusters: {len(cluster_sizes)}")
    print(f"  Scattered clusters (< 3 APIs): {scattered_count}")

    # Show scattered clusters
    print("\nScattered clusters:")
    for cluster_id, size in sorted(cluster_sizes.items()):
        if size < 3:
            apis = [api for api in clustered_apis if api['cluster'] == cluster_id]
            entity = apis[0].get('entity_anchor', 'unknown')
            print(f"  Cluster {cluster_id}: {entity} ({size} APIs)")
            for api in apis:
                path = api.get('path', '').split('/')[-2:]
                print(f"    - {api['method']} .../{'/'.join(path)}")

    # Step 2: Apply LLM refiner
    print("\n" + "=" * 80)
    print("[2] Applying LLM refiner...")
    print("=" * 80)

    refiner = LLMClusterRefiner(
        min_cluster_size=3,
        use_openai=False  # Set to True if you have OpenAI API key
    )

    refined_apis = refiner.refine(clustered_apis)

    # Show refined statistics
    refined_cluster_sizes = defaultdict(int)
    for api in refined_apis:
        refined_cluster_sizes[api['cluster']] += 1

    refined_scattered_count = sum(1 for size in refined_cluster_sizes.values() if size < 3)

    print("\n" + "=" * 80)
    print("[3] Refinement Results")
    print("=" * 80)
    print(f"\nRefined clustering:")
    print(f"  Total APIs: {len(refined_apis)}")
    print(f"  Total clusters: {len(refined_cluster_sizes)}")
    print(f"  Scattered clusters (< 3 APIs): {refined_scattered_count}")
    print(f"  Improvement: {scattered_count - refined_scattered_count} fewer scattered clusters")

    # Show LLM-modified APIs
    print("\n" + "=" * 80)
    print("[4] LLM Modifications")
    print("=" * 80)

    llm_modified = [api for api in refined_apis if 'llm_reason' in api]
    if llm_modified:
        print(f"\nFound {len(llm_modified)} APIs modified by LLM:\n")

        for api in llm_modified:
            path = api.get('path', '').split('/')[-2:]
            cluster_type = api.get('cluster_type', 'unknown')
            reason = api.get('llm_reason', 'No reason provided')

            print(f"  {api['method']} .../{'/'.join(path)}")
            print(f"    Type: {cluster_type}")
            print(f"    Cluster: {api['cluster']}")
            print(f"    Reason: {reason}")
            print()
    else:
        print("\nNo APIs were modified by LLM (LLM may not be available)")
        print("Tip: Set use_openai=True and provide API key, or run local LLM (Ollama)")

    # Step 3: Export refined result
    print("\n" + "=" * 80)
    print("[5] Exporting refined result...")
    print("=" * 80)

    # Extract capabilities from refined clusters
    capabilities_result = service.extractor.extract(refined_apis)

    result = {
        'capabilities': capabilities_result['capabilities'],
        'statistics': {
            'total_apis': capabilities_result['total_apis'],
            'total_capabilities': capabilities_result['total_capabilities'],
            'scattered_before': scattered_count,
            'scattered_after': refined_scattered_count,
            'llm_modified': len(llm_modified)
        },
        'source': {
            'title': parsed['title'],
            'version': parsed['version'],
            'source': 'erp-server.json'
        }
    }

    output_path = 'erp-server-refined.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nRefined result exported to: {output_path}")

    # Show some refined capabilities
    print("\n" + "=" * 80)
    print("[6] Sample Refined Capabilities")
    print("=" * 80)

    for i, cap in enumerate(capabilities_result['capabilities'][:5]):
        print(f"\n{i+1}. {cap['name']}")
        print(f"   Resource: {cap.get('resource', 'N/A')}")
        print(f"   APIs: {cap['api_count']}")
        print(f"   Type: {cap.get('type', 'composite')}")

    print("\n" + "=" * 80)
    print("Test completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
