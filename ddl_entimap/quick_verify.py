"""
EntiMap 快速验证脚本 - 不调用LLM，仅验证数据库连接和元数据提取
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ddl_entimap import EntiMapEngine
from urllib.parse import quote_plus
import json


def main():
    print("=" * 60)
    print("EntiMap 快速验证")
    print("=" * 60)

    # 配置数据库连接
    password = quote_plus("LDPP@MySQL82024!")
    db_url = f"mysql+pymysql://root:{password}@192.168.1.33:8888/eqiai_erp"

    # 初始化引擎（不需要API密钥，因为我们不调用LLM）
    engine = EntiMapEngine(
        db_url=db_url,
        api_key="dummy",  # 占位符
        model="qwen-plus",
        output_dir="./entimap_output"
    )

    # 步骤1: 测试数据库连接
    print("\n[步骤1] 测试数据库连接...")
    try:
        tables = engine.profiler.get_all_tables()
        print(f"[OK] 成功连接到数据库")
        print(f"[OK] 找到 {len(tables)} 张表")
        print(f"[OK] 表列表: {tables}")
    except Exception as e:
        print(f"[FAIL] 数据库连接失败: {e}")
        return

    # 步骤2: 提取所有表的元数据
    print(f"\n[步骤2] 提取所有表的元数据...")
    try:
        profiles = engine.profile_database(cache_path="./table_profiles_cache.json")
        print(f"[OK] 成功提取 {len(profiles)} 张表的元数据")
        print(f"[OK] 已缓存到 table_profiles_cache.json")
    except Exception as e:
        print(f"[FAIL] 元数据提取失败: {e}")
        import traceback
        traceback.print_exc()
        return

    # 步骤3: 显示示例表的详细信息
    print(f"\n[步骤3] 显示示例表信息...")
    if tables:
        sample_table = tables[0]
        profile = profiles[sample_table]

        print(f"\n表名: {sample_table}")
        print(f"  行数: {profile['stats']['row_count']}")
        print(f"  列数: {profile['stats']['column_count']}")
        print(f"  主键: {profile['ddl']['primary_keys']}")
        print(f"  外键数: {len(profile['ddl']['foreign_keys'])}")

        print(f"\n  前5个字段:")
        for col in profile['ddl']['columns'][:5]:
            comment = col.get('comment', '')
            print(f"    - {col['name']} ({col['type']}) {f'-- {comment}' if comment else ''}")

        if profile['samples']:
            print(f"\n  数据采样 (前1行):")
            print(f"    {json.dumps(profile['samples'][0], ensure_ascii=False, default=str)[:200]}...")

    # 步骤4: 加载API实体
    print(f"\n[步骤4] 加载API实体...")
    entities_path = os.path.join(os.path.dirname(__file__), "entities.json")
    try:
        entities = engine.load_api_entities(entities_path)
        print(f"[OK] 成功加载 {len(entities)} 个实体")
        print(f"[OK] 实体列表:")
        for i, entity in enumerate(entities[:5], 1):
            print(f"  {i}. {entity['name']} - {len(entity['api_fields'])} 个字段, {len(entity['api_paths'])} 个API")
        if len(entities) > 5:
            print(f"  ... 还有 {len(entities) - 5} 个实体")
    except Exception as e:
        print(f"[FAIL] 加载实体失败: {e}")
        entities = []

    # 总结
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)
    print(f"数据库: {len(tables)} 张表")
    print(f"实体: {len(entities)} 个")
    print(f"元数据已缓存到: table_profiles_cache.json")
    print("\n下一步:")
    print("1. 设置环境变量: export DASHSCOPE_API_KEY=your-api-key")
    print("2. 运行完整流程: python example_usage.py")


if __name__ == "__main__":
    main()
