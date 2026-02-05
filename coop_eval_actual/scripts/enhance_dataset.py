"""
增强数据集：
1. 根据跨业务系统数量重新计算 level
2. 为每个任务添加 prompt_brief（简短模糊的用户指令）
"""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import calculate_cross_system_level


# 简短 prompt 映射：task_id -> prompt_brief
# 这些是真实用户可能说的简短、模糊的指令
BRIEF_PROMPTS = {
    1: "新品上市前的准备工作",
    2: "查一下客户和价格",
    3: "更新产品分类，顺便看看供应商和退货情况",
    4: "看看仓库调拨和布局",
    5: "给新产品生成SKU",
    6: "清理客户数据，查下出库单",
    7: "大客户项目启动准备",
    8: "做个库存分析报告",
    9: "处理库存差异和订单拦截问题",
    10: "更新采购单，看下仓库情况",
    11: "季度供应商评估",
    12: "查本月收款情况",
    13: "大促备货检查",
    14: "处理客户退货投诉",
    15: "新品定价",
    16: "月底销售汇总",
    17: "出库操作",
    18: "渠道拓展",
    19: "新品导入",
    20: "供应商合同谈判",
    21: "优化仓库管理",
    22: "跟进新商机",
    23: "年度产品规划",
    24: "月度对账",
    25: "新货入库",
    26: "处理新订单",
    27: "做MRP计划",
    28: "调整产品状态",
    29: "更新大客户信息",
    30: "仓库单据审核",
    31: "清理停产产品",
    32: "处理超额订单",
    33: "库存盘点调整",
    34: "调整产品价格",
    35: "取消发货单",
    36: "年终盘点",
    37: "归档退货单",
    38: "维护产品单位",
    39: "新建仓库",
    40: "修改销售订单",
    41: "整理产品分类",
    42: "处理采购退货",
    43: "准备跨部门会议资料",
    44: "完成出库",
    45: "新客户开户",
    46: "跟进采购流程",
    47: "完善产品主数据",
    48: "关闭仓库",
    49: "处理发货流程",
    50: "取消库存调拨",
}


def enhance_dataset(input_path: str, output_path: str):
    """增强数据集"""
    with open(input_path, 'r', encoding='utf-8') as f:
        tasks = json.load(f)

    enhanced_tasks = []
    for task in tasks:
        task_id = task['task_id']
        expected_agents = task.get('expected_agents', [])

        # 重新计算 level（基于跨系统数量）
        new_level = calculate_cross_system_level(expected_agents)

        # 获取简短 prompt
        prompt_brief = BRIEF_PROMPTS.get(task_id, f"任务{task_id}")

        # 提取涉及的系统
        systems = set()
        for agent_id in expected_agents:
            parts = agent_id.split("__")
            if parts:
                systems.add(parts[0])

        enhanced_task = {
            "task_id": task_id,
            "level": new_level,
            "systems": sorted(list(systems)),
            "num_agents": len(expected_agents),
            "prompt": task['prompt'],  # 详细描述（原有）
            "prompt_brief": prompt_brief,  # 简短模糊指令（新增）
            "expected_agents": expected_agents,
        }
        enhanced_tasks.append(enhanced_task)

    # 按 level 排序
    enhanced_tasks.sort(key=lambda x: (x['level'], x['task_id']))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_tasks, f, ensure_ascii=False, indent=2)

    # 打印统计
    print(f"Enhanced {len(enhanced_tasks)} tasks")
    print("\nLevel distribution:")
    level_counts = {}
    for task in enhanced_tasks:
        level = task['level']
        level_counts[level] = level_counts.get(level, 0) + 1
    for level in sorted(level_counts.keys()):
        print(f"  Level {level}: {level_counts[level]} tasks")

    print("\nSample tasks by level:")
    for level in sorted(level_counts.keys()):
        sample = next(t for t in enhanced_tasks if t['level'] == level)
        print(f"\n  Level {level} (跨{level}个系统):")
        print(f"    Systems: {sample['systems']}")
        print(f"    Brief: {sample['prompt_brief']}")
        print(f"    Detailed: {sample['prompt'][:60]}...")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="coop_eval_actual/data/dataset_erp_v2.json")
    parser.add_argument("--output", default="coop_eval_actual/data/dataset_erp_v3.json")
    args = parser.parse_args()

    enhance_dataset(args.input, args.output)
