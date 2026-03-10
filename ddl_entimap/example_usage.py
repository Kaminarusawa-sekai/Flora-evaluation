"""
EntiMap 使用示例

演示如何使用EntiMap引擎进行数据库到业务实体的自动化对齐
"""

from ddl_entimap import EntiMapEngine
import os
from urllib.parse import quote_plus


def example_full_pipeline():
    """示例1: 运行完整的端到端流程"""

    # URL编码密码中的特殊字符
    password = quote_plus("LDPP@MySQL82024!")
    db_url = f"mysql+pymysql://root:{password}@192.168.1.33:8888/eqiai_erp"

    # 初始化引擎
    engine = EntiMapEngine(
        db_url=db_url,
        api_key=os.environ["DASHSCOPE_API_KEY"],  # 从环境变量获取API密钥
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 如果使用兼容OpenAI的服务，填写base_url
        model="qwen-plus",
        output_dir="./entimap_output"
    )

    # 运行完整流程
    # entities.json 格式示例见下方
    engine.run_full_pipeline(
        entities_path="./entities.json",
        cache_profiles=True,
        top_k_tables=10
    )


def example_quick_align():
    """示例2: 快速对齐单个实体"""

    engine = EntiMapEngine(
        db_url="mysql://user:password@localhost:3306/your_database",
        api_key="your-openai-api-key",
        output_dir="./entimap_output"
    )

    # 快速对齐用户实体
    results = engine.quick_align(
        entity_name="User",
        entity_description="系统用户实体，包含用户基本信息和账号信息",
        api_fields=[
            {"name": "userId", "description": "用户ID"},
            {"name": "userName", "description": "用户名"},
            {"name": "phoneNumber", "description": "手机号"},
            {"name": "email", "description": "邮箱"},
            {"name": "departmentName", "description": "部门名称"}
        ],
        top_k=5
    )

    # 查看结果
    for table_name, result in results.items():
        print(f"\n表: {table_name}")
        print(f"匹配度: {result['relation_score']}")
        print(f"关系类型: {result['relation_type']}")
        print(f"业务字段: {result['columns_role']['business']}")


def example_step_by_step():
    """示例3: 分步执行（适合调试）"""

    engine = EntiMapEngine(
        db_url="mysql://user:password@localhost:3306/your_database",
        api_key="your-openai-api-key",
        output_dir="./entimap_output"
    )

    # Step 1: 提取数据库元数据（只需执行一次，可以缓存）
    print("Step 1: Profiling database...")
    engine.profile_database(cache_path="./table_profiles.json")

    # 后续可以直接加载缓存
    # engine.load_cached_profiles("./table_profiles.json")

    # Step 2: 加载API实体
    entities = engine.load_api_entities("./entities.json")

    # Step 3: 逐个实体对齐
    for entity in entities:
        print(f"\nProcessing entity: {entity['name']}")

        # 对齐
        alignment_results = engine.align_entity(entity, top_k=10)

        # 导出
        engine.export_results(
            entity['name'],
            alignment_results,
            export_format="all",
            generate_sql=True
        )

    # 查看摘要
    summary = engine.get_summary()
    print(f"\nSummary: {summary}")


def example_with_qwen():
    """示例4: 使用通义千问等兼容OpenAI的服务"""

    engine = EntiMapEngine(
        db_url="mysql://user:password@localhost:3306/your_database",
        api_key="your-qwen-api-key",
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 通义千问的兼容端点
        model="qwen-max",  # 或 qwen-plus, qwen-turbo
        output_dir="./entimap_output"
    )

    engine.run_full_pipeline(
        entities_path="./entities.json",
        cache_profiles=True,
        top_k_tables=10
    )


if __name__ == "__main__":
    # 选择一个示例运行
    # example_full_pipeline()
    # example_quick_align()
    # example_step_by_step()
    # example_with_qwen()

    print("""
    EntiMap 使用示例

    请根据你的需求选择合适的示例：
    1. example_full_pipeline() - 完整的端到端流程
    2. example_quick_align() - 快速对齐单个实体
    3. example_step_by_step() - 分步执行（适合调试）
    4. example_with_qwen() - 使用通义千问等兼容服务

    使用前请修改：
    - 数据库连接字符串 (db_url)
    - API密钥 (api_key)
    - 实体定义文件路径 (entities_path)
    """)


"""
entities.json 格式示例：

[
  {
    "name": "User",
    "description": "系统用户实体，包含用户基本信息和账号信息",
    "api_fields": [
      {
        "name": "userId",
        "description": "用户ID",
        "type": "string"
      },
      {
        "name": "userName",
        "description": "用户名",
        "type": "string"
      },
      {
        "name": "phoneNumber",
        "description": "手机号",
        "type": "string"
      },
      {
        "name": "email",
        "description": "邮箱",
        "type": "string"
      },
      {
        "name": "departmentName",
        "description": "所属部门",
        "type": "string"
      }
    ],
    "api_paths": [
      "/api/user/list",
      "/api/user/info",
      "/api/user/create"
    ]
  },
  {
    "name": "Order",
    "description": "订单实体，包含订单基本信息和状态",
    "api_fields": [
      {
        "name": "orderId",
        "description": "订单ID",
        "type": "string"
      },
      {
        "name": "orderNo",
        "description": "订单号",
        "type": "string"
      },
      {
        "name": "totalAmount",
        "description": "订单总金额",
        "type": "number"
      },
      {
        "name": "status",
        "description": "订单状态",
        "type": "string"
      },
      {
        "name": "createTime",
        "description": "创建时间",
        "type": "string"
      }
    ],
    "api_paths": [
      "/api/order/list",
      "/api/order/detail"
    ]
  }
]
"""
