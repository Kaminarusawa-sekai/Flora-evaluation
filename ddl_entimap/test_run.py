"""
测试 EntiMap 引擎 - 使用 ERP 数据库
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ddl_entimap import EntiMapEngine
from urllib.parse import quote_plus


def test_connection():
    """测试数据库连接"""
    print("=" * 60)
    print("测试数据库连接")
    print("=" * 60)

    try:
        # URL编码密码中的特殊字符
        password = quote_plus("LDPP@MySQL82024!")
        db_url = f"mysql+pymysql://root:{password}@192.168.1.33:8888/eqiai_erp"

        engine = EntiMapEngine(
            db_url=db_url,
            api_key=os.environ.get("DASHSCOPE_API_KEY", ""),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-plus",
            output_dir="./entimap_output"
        )

        # 测试获取表列表
        tables = engine.profiler.get_all_tables()
        print(f"[OK] 数据库连接成功！")
        print(f"[OK] 找到 {len(tables)} 张表")
        print(f"[OK] 前10张表: {tables[:10]}")

        return True
    except Exception as e:
        print(f"[FAIL] 数据库连接失败: {e}")
        return False


def test_profile_single_table():
    """测试提取单张表的元数据"""
    print("\n" + "=" * 60)
    print("测试提取表元数据")
    print("=" * 60)

    try:
        password = quote_plus("LDPP@MySQL82024!")
        db_url = f"mysql+pymysql://root:{password}@192.168.1.33:8888/eqiai_erp"

        engine = EntiMapEngine(
            db_url=db_url,
            api_key=os.environ.get("DASHSCOPE_API_KEY", ""),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-plus",
            output_dir="./entimap_output"
        )

        tables = engine.profiler.get_all_tables()
        if tables:
            test_table = tables[0]
            print(f"\n测试表: {test_table}")

            profile = engine.profiler.profile_table(test_table)
            print(f"[OK] DDL提取成功: {len(profile['ddl']['columns'])} 个字段")
            print(f"[OK] 数据采样: {len(profile['samples'])} 行")
            print(f"[OK] 统计信息: {profile['stats']['row_count']} 行数据")

            # 显示字段信息
            print(f"\n字段列表:")
            for col in profile['ddl']['columns'][:5]:
                print(f"  - {col['name']} ({col['type']}): {col.get('comment', '')}")

            return True
    except Exception as e:
        print(f"[FAIL] 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_quick_align():
    """测试快速对齐单个实体"""
    print("\n" + "=" * 60)
    print("测试快速对齐实体")
    print("=" * 60)

    try:
        password = quote_plus("LDPP@MySQL82024!")
        db_url = f"mysql+pymysql://root:{password}@192.168.1.33:8888/eqiai_erp"

        engine = EntiMapEngine(
            db_url=db_url,
            api_key=os.environ.get("DASHSCOPE_API_KEY", ""),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen-plus",
            output_dir="./entimap_output"
        )

        print("\n正在对齐 'Purchase Order' 实体...")
        results = engine.quick_align(
            entity_name="Purchase Order",
            entity_description="采购订单管理，包含采购单的创建、查询、更新、删除功能",
            api_fields=[
                {"name": "no", "description": "采购单编号"},
                {"name": "supplierId", "description": "供应商编号"},
                {"name": "orderTime", "description": "采购时间"},
                {"name": "status", "description": "采购状态"},
                {"name": "productId", "description": "产品编号"}
            ],
            top_k=3
        )

        print(f"\n[OK] 对齐完成！找到 {len(results)} 张相关表")

        for table_name, result in results.items():
            print(f"\n表: {table_name}")
            print(f"  匹配度: {result['relation_score']}/100")
            print(f"  关系类型: {result['relation_type']}")
            print(f"  业务字段: {result['columns_role']['business'][:5]}")
            print(f"  技术字段: {result['columns_role']['technical'][:3]}")
            print(f"  隐藏逻辑: {result['columns_role']['hidden_logic']}")

        return True
    except Exception as e:
        print(f"[FAIL] 对齐失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("EntiMap 测试脚本")
    print("=" * 60)

    # 检查API密钥
    if not os.environ.get("DASHSCOPE_API_KEY"):
        print("警告: 未设置 DASHSCOPE_API_KEY 环境变量")
        print("某些测试可能会失败")

    # 运行测试
    test_results = []

    test_results.append(("数据库连接", test_connection()))
    test_results.append(("表元数据提取", test_profile_single_table()))
    test_results.append(("实体对齐", test_quick_align()))

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for name, result in test_results:
        status = "[OK] 通过" if result else "[FAIL] 失败"
        print(f"{status}: {name}")
