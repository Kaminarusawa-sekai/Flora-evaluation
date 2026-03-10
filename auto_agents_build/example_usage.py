"""
示例用法 - 完整流水线执行
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from orchestrator import PipelineOrchestrator, Validator, ReportGenerator


def main():
    """主函数"""

    # 示例输入：API 能力列表
    api_capabilities = [
        {
            "id": "api_001",
            "name": "创建订单",
            "description": "创建新的销售订单",
            "method": "POST",
            "path": "/api/order/create",
            "tags": ["订单", "销售"]
        },
        {
            "id": "api_002",
            "name": "查询订单",
            "description": "查询订单信息",
            "method": "GET",
            "path": "/api/order/query",
            "tags": ["订单", "查询"]
        },
        {
            "id": "api_003",
            "name": "更新订单",
            "description": "更新订单状态",
            "method": "PUT",
            "path": "/api/order/update",
            "tags": ["订单", "更新"]
        },
        {
            "id": "api_004",
            "name": "删除订单",
            "description": "删除订单",
            "method": "DELETE",
            "path": "/api/order/delete",
            "tags": ["订单", "删除"]
        },
        {
            "id": "api_005",
            "name": "查询客户",
            "description": "查询客户信息",
            "method": "GET",
            "path": "/api/customer/query",
            "tags": ["客户", "查询"]
        },
        {
            "id": "api_006",
            "name": "创建客户",
            "description": "创建新客户",
            "method": "POST",
            "path": "/api/customer/create",
            "tags": ["客户", "创建"]
        },
        {
            "id": "api_007",
            "name": "查询库存",
            "description": "查询库存信息",
            "method": "GET",
            "path": "/api/inventory/query",
            "tags": ["库存", "查询"]
        },
        {
            "id": "api_008",
            "name": "更新库存",
            "description": "更新库存数量",
            "method": "PUT",
            "path": "/api/inventory/update",
            "tags": ["库存", "更新"]
        }
    ]

    print("=" * 80)
    print("Agent 自动化构建系统 - 示例运行")
    print("=" * 80)
    print()

    # 1. 验证输入
    print("步骤 1: 验证输入...")
    validator = Validator()
    is_valid, errors = validator.validate_input(api_capabilities)

    if not is_valid:
        print("输入验证失败:")
        for error in errors:
            print(f"  - {error}")
        return

    print(f"✓ 输入验证通过: {len(api_capabilities)} 个 API")
    print()

    # 2. 运行流水线
    print("步骤 2: 运行构建流水线...")
    print()

    orchestrator = PipelineOrchestrator()
    result = orchestrator.run_pipeline(api_capabilities, output_dir="./output")

    print()

    # 3. 验证输出
    print("步骤 3: 验证输出...")
    is_valid, errors = validator.validate_pipeline_result(result)

    if not is_valid:
        print("输出验证失败:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ 输出验证通过")

    print()

    # 4. 生成报告
    print("步骤 4: 生成报告...")
    report_generator = ReportGenerator()

    # 文本报告
    report = report_generator.generate_report(result)
    report_generator.save_report(report, "./output/build_report.txt")
    print("✓ 文本报告已保存: ./output/build_report.txt")

    # HTML 报告
    report_generator.save_html_report(result, "./output/build_report.html")
    print("✓ HTML 报告已保存: ./output/build_report.html")

    print()
    print("=" * 80)
    print("构建完成！")
    print("=" * 80)
    print()
    print("输出文件:")
    print("  - output/layer2/role_manifest.json")
    print("  - output/layer3/org_blueprint.json")
    print("  - output/layer4/prompts/")
    print("  - output/layer4/manifest.json")
    print("  - output/build_report.txt")
    print("  - output/build_report.html")


if __name__ == "__main__":
    main()
