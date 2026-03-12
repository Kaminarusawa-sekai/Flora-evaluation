"""测试 entity 命名是否完整"""

import sys
from pathlib import Path
from collections import Counter

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from adapters.normalization_adapter import NormalizationAdapter


def test_entity_naming():
    """测试所有 API 是否都有正确的 entity 命名"""
    
    print("="*80)
    print("测试 Entity 命名完整性")
    print("="*80)
    
    # 配置
    config = {
        'use_hdbscan': True,
        'use_prance': True,
        'enable_evaluation': False,
        'use_entity_clustering': True,
        'entity_similarity_threshold': 0.85,
        'use_llm_refiner': True,
        'llm_refiner_config': {
            'llm_provider': 'qwen',
            'model': 'qwen-plus',
            'min_cluster_size': 3
        }
    }
    
    # 输入数据
    input_data = 'erp-server.json'
    
    # 创建 adapter
    adapter = NormalizationAdapter()
    
    print("\n开始处理...")
    result = adapter.process(input_data, config)
    
    print("\n" + "="*80)
    print("Entity 命名检查结果")
    print("="*80)
    
    # 统计 entity 分布
    all_entities = []
    unknown_count = 0
    
    for capability in result.capabilities:
        for api in capability.apis:
            entity = getattr(api, 'entity_anchor', 'unknown')
            all_entities.append(entity)
            if entity == 'unknown':
                unknown_count += 1
                print(f"⚠️  未命名的 API: {api.method} {api.path}")
    
    # 统计
    entity_counts = Counter(all_entities)
    
    print(f"\n总 API 数: {len(all_entities)}")
    print(f"不同 entity 数: {len(entity_counts)}")
    print(f"未命名 (unknown) 的 API 数: {unknown_count}")
    
    print(f"\nEntity 分布 (Top 10):")
    for entity, count in entity_counts.most_common(10):
        print(f"  {entity}: {count} APIs")
    
    # 判断是否通过
    if unknown_count == 0:
        print("\n✅ 测试通过：所有 API 都有正确的 entity 命名")
        return True
    else:
        print(f"\n❌ 测试失败：仍有 {unknown_count} 个 API 未正确命名")
        return False


if __name__ == '__main__':
    try:
        success = test_entity_naming()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
