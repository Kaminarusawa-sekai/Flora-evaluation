"""简单示例：使用LLM Refiner处理离散API"""

import sys
import io
from pathlib import Path

# Fix Windows encoding issue
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

from api_normalization import NormalizationService
from api_normalization.llm_cluster_refiner import LLMClusterRefiner
from collections import defaultdict


def main():
    # ==================== 配置区域 ====================
    # 修改这里来使用不同的LLM提供商

    # 选项1: Rule-based (默认，无需配置)
    # LLM_PROVIDER = "rule"
    # MODEL = None

    # 选项2: Qwen (通义千问) - 推荐国内用户
    LLM_PROVIDER = "qwen"
    MODEL = "qwen-plus"  # 或 "qwen-turbo", "qwen-max"
    import os
    os.environ['QWEN_API_KEY'] = os.getenv("DASHSCOPE_API_KEY", "")

    # 选项3: DeepSeek - 推荐代码分析
    # LLM_PROVIDER = "deepseek"
    # MODEL = "deepseek-coder"  # 或 "deepseek-chat"
    # import os
    # os.environ['DEEPSEEK_API_KEY'] = 'sk-your-key'

    # 选项4: Ollama (本地) - 免费
    # LLM_PROVIDER = "ollama"
    # MODEL = "qwen2.5:7b"  # 或其他已下载的模型

    # 选项5: OpenAI
    # LLM_PROVIDER = "openai"
    # MODEL = "gpt-4"  # 或 "gpt-3.5-turbo"
    # import os
    # os.environ['OPENAI_API_KEY'] = 'sk-your-key'

    # 选项6: Zhipu AI (GLM)
    # LLM_PROVIDER = "zhipu"
    # MODEL = "glm-4"
    # import os
    # os.environ['ZHIPU_API_KEY'] = 'your-key'

    SWAGGER_FILE = 'erp-server.json'
    # ==================== 配置结束 ====================

    print("开始处理API聚类...")
    print(f"LLM提供商: {LLM_PROVIDER}")
    if MODEL:
        print(f"模型: {MODEL}")

    # Step 1: 初始聚类
    print("\n[1/3] 初始聚类...")
    service = NormalizationService(
        use_entity_clustering=True,
        entity_similarity_threshold=0.85,
        enable_evaluation=False
    )

    parsed = service.parser.parse(SWAGGER_FILE)
    clustered_apis = service.clusterer.cluster(parsed['apis'])

    # 统计初始状态
    cluster_sizes = defaultdict(int)
    for api in clustered_apis:
        cluster_sizes[api['cluster']] += 1

    scattered_before = sum(1 for size in cluster_sizes.values() if size < 3)
    print(f"   总API数: {len(clustered_apis)}")
    print(f"   总集群数: {len(cluster_sizes)}")
    print(f"   离散集群数 (< 3 APIs): {scattered_before}")

    # Step 2: 应用LLM Refiner
    print("\n[2/3] 应用LLM Refiner...")

    refiner_kwargs = {
        'llm_provider': LLM_PROVIDER,
        'min_cluster_size': 3
    }
    if MODEL:
        refiner_kwargs['model'] = MODEL

    refiner = LLMClusterRefiner(**refiner_kwargs)

    refined_apis = refiner.refine(clustered_apis)

    # 统计改进后状态
    refined_cluster_sizes = defaultdict(int)
    for api in refined_apis:
        refined_cluster_sizes[api['cluster']] += 1

    scattered_after = sum(1 for size in refined_cluster_sizes.values() if size < 3)
    improvement = scattered_before - scattered_after

    print(f"\n   改进后集群数: {len(refined_cluster_sizes)}")
    print(f"   离散集群数: {scattered_after}")
    print(f"   改进: 减少了 {improvement} 个离散集群")

    # Step 3: 显示新创建的组
    print("\n[3/3] 新创建的API组:")

    # 找出新创建的集群（ID >= 1000）
    new_clusters = defaultdict(list)
    for api in refined_apis:
        cluster_id = api['cluster']
        if cluster_id >= 1000:
            new_clusters[cluster_id].append(api)

    if new_clusters:
        for cluster_id, apis in sorted(new_clusters.items()):
            print(f"\n   Cluster {cluster_id} ({len(apis)} APIs):")
            reason = apis[0].get('llm_reason', 'No reason')
            print(f"      理由: {reason}")
            for api in apis[:5]:  # 只显示前5个
                path_parts = api.get('path', '').split('/')[-2:]
                print(f"      - {api['method']} .../{'/'.join(path_parts)}")
            if len(apis) > 5:
                print(f"      ... 还有 {len(apis) - 5} 个API")
    else:
        print("   没有创建新的集群（所有API已经分组良好）")

    # 显示保持原子的API
    atomic_apis = [api for api in refined_apis
                   if api.get('cluster_type') in ['atomic', 'llm_atomic']]

    if atomic_apis:
        print(f"\n   保持为原子API的数量: {len(atomic_apis)}")
        print("   示例:")
        for api in atomic_apis[:3]:
            path_parts = api.get('path', '').split('/')[-2:]
            print(f"      - {api['method']} .../{'/'.join(path_parts)}")

    # 导出结果
    print("\n" + "="*60)
    print("处理完成！")
    print("="*60)

    # 提取capabilities
    capabilities_result = service.extractor.extract(refined_apis)

    print(f"\n最终结果:")
    print(f"  - 总Capabilities: {capabilities_result['total_capabilities']}")
    print(f"  - 语义Capabilities: {capabilities_result.get('semantic_capabilities', 0)}")
    print(f"  - 原子Capabilities: {capabilities_result.get('atomic_capabilities', 0)}")

    # 保存结果
    import json
    output_file = 'erp-server-refined.json'
    result = {
        'capabilities': capabilities_result['capabilities'],
        'statistics': {
            'total_apis': len(refined_apis),
            'total_capabilities': capabilities_result['total_capabilities'],
            'scattered_before': scattered_before,
            'scattered_after': scattered_after,
            'improvement': improvement
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n结果已保存到: {output_file}")


if __name__ == '__main__':
    main()
