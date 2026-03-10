"""测试不同LLM提供商的API聚类效果"""

import sys
import io
from pathlib import Path

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent.parent))

from api_normalization import NormalizationService
from api_normalization.llm_cluster_refiner import LLMClusterRefiner
from collections import defaultdict
import os


def test_provider(provider_name: str, **kwargs):
    """测试单个LLM提供商"""
    print("\n" + "="*80)
    print(f"测试提供商: {provider_name.upper()}")
    print("="*80)

    try:
        # 初始聚类
        service = NormalizationService(
            use_entity_clustering=True,
            entity_similarity_threshold=0.85,
            enable_evaluation=False
        )

        parsed = service.parser.parse('erp-server.json')
        clustered_apis = service.clusterer.cluster(parsed['apis'])

        # 统计初始状态
        cluster_sizes = defaultdict(int)
        for api in clustered_apis:
            cluster_sizes[api['cluster']] += 1

        scattered_before = sum(1 for size in cluster_sizes.values() if size < 3)

        # 应用LLM refiner
        refiner = LLMClusterRefiner(
            llm_provider=provider_name,
            min_cluster_size=3,
            **kwargs
        )

        refined_apis = refiner.refine(clustered_apis)

        # 统计改进后状态
        refined_cluster_sizes = defaultdict(int)
        for api in refined_apis:
            refined_cluster_sizes[api['cluster']] += 1

        scattered_after = sum(1 for size in refined_cluster_sizes.values() if size < 3)
        improvement = scattered_before - scattered_after

        print(f"\n结果:")
        print(f"  离散集群: {scattered_before} -> {scattered_after}")
        print(f"  改进: {improvement} 个集群")
        print(f"  状态: ✓ 成功")

        return True

    except Exception as e:
        print(f"\n错误: {e}")
        print(f"  状态: ✗ 失败")
        return False


def main():
    print("="*80)
    print("LLM Provider 测试")
    print("="*80)
    print("\n这个脚本会测试不同的LLM提供商")
    print("如果某个提供商不可用，会自动跳过\n")

    results = {}

    # 1. Rule-based (总是可用)
    print("\n[1/7] 测试 Rule-based (默认)")
    results['rule'] = test_provider('rule')

    # 2. OpenAI (如果有API key)
    print("\n[2/7] 测试 OpenAI")
    if os.getenv('OPENAI_API_KEY'):
        results['openai'] = test_provider('openai', model='gpt-3.5-turbo')
    else:
        print("跳过: 未设置 OPENAI_API_KEY")
        results['openai'] = None

    # 3. Qwen (如果有API key)
    print("\n[3/7] 测试 Qwen (通义千问)")
    if os.getenv('QWEN_API_KEY'):
        results['qwen'] = test_provider('qwen', model='qwen-plus')
    else:
        print("跳过: 未设置 QWEN_API_KEY")
        print("提示: 访问 https://dashscope.console.aliyun.com/ 获取")
        results['qwen'] = None

    # 4. DeepSeek (如果有API key)
    print("\n[4/7] 测试 DeepSeek")
    if os.getenv('DEEPSEEK_API_KEY'):
        results['deepseek'] = test_provider('deepseek', model='deepseek-chat')
    else:
        print("跳过: 未设置 DEEPSEEK_API_KEY")
        print("提示: 访问 https://platform.deepseek.com/ 获取")
        results['deepseek'] = None

    # 5. Zhipu (如果有API key)
    print("\n[5/7] 测试 Zhipu AI (GLM)")
    if os.getenv('ZHIPU_API_KEY'):
        results['zhipu'] = test_provider('zhipu', model='glm-4')
    else:
        print("跳过: 未设置 ZHIPU_API_KEY")
        print("提示: 访问 https://open.bigmodel.cn/ 获取")
        results['zhipu'] = None

    # 6. Ollama (如果服务在运行)
    print("\n[6/7] 测试 Ollama (本地)")
    try:
        import requests
        response = requests.get('http://localhost:11434/api/tags', timeout=2)
        if response.status_code == 200:
            # 检查是否有可用模型
            models = response.json().get('models', [])
            if models:
                model_name = models[0]['name']
                print(f"找到本地模型: {model_name}")
                results['ollama'] = test_provider('ollama', model=model_name)
            else:
                print("跳过: Ollama没有已下载的模型")
                print("提示: 运行 'ollama pull qwen2.5:7b' 下载模型")
                results['ollama'] = None
        else:
            print("跳过: Ollama服务未响应")
            results['ollama'] = None
    except Exception as e:
        print(f"跳过: Ollama不可用 ({e})")
        print("提示: 运行 'ollama serve' 启动服务")
        results['ollama'] = None

    # 7. OpenAI-compatible (示例)
    print("\n[7/7] 测试 OpenAI-compatible API")
    print("跳过: 需要自定义配置")
    results['openai-compatible'] = None

    # 总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)

    success_count = sum(1 for v in results.values() if v is True)
    skip_count = sum(1 for v in results.values() if v is None)
    fail_count = sum(1 for v in results.values() if v is False)

    print(f"\n总计: {len(results)} 个提供商")
    print(f"  ✓ 成功: {success_count}")
    print(f"  - 跳过: {skip_count}")
    print(f"  ✗ 失败: {fail_count}")

    print("\n详细结果:")
    for provider, result in results.items():
        if result is True:
            status = "✓ 成功"
        elif result is None:
            status = "- 跳过"
        else:
            status = "✗ 失败"
        print(f"  {provider:20} {status}")

    # 推荐
    print("\n" + "="*80)
    print("推荐配置")
    print("="*80)

    if results.get('qwen'):
        print("\n✓ 推荐使用 Qwen (通义千问)")
        print("  - 中文友好")
        print("  - 性价比高")
        print("  - 国内访问快")
    elif results.get('deepseek'):
        print("\n✓ 推荐使用 DeepSeek")
        print("  - 代码分析专用")
        print("  - 性价比高")
    elif results.get('ollama'):
        print("\n✓ 推荐使用 Ollama (本地)")
        print("  - 完全免费")
        print("  - 隐私保护")
        print("  - 无需API key")
    else:
        print("\n✓ 推荐使用 Rule-based")
        print("  - 无需配置")
        print("  - 快速稳定")
        print("  - 适合生产环境")

    print("\n配置示例:")
    print("```python")
    if results.get('qwen'):
        print("refiner = LLMClusterRefiner(")
        print("    llm_provider='qwen',")
        print("    model='qwen-plus'")
        print(")")
    elif results.get('ollama'):
        print("refiner = LLMClusterRefiner(")
        print("    llm_provider='ollama',")
        print("    model='qwen2.5:7b'")
        print(")")
    else:
        print("refiner = LLMClusterRefiner(")
        print("    llm_provider='rule'")
        print(")")
    print("```")

    print("\n" + "="*80)


if __name__ == '__main__':
    main()
