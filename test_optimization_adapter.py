"""
测试 OptimizationAdapter 直接调用功能
"""

from adapters.optimization_adapter import OptimizationAdapter
from schemas.schemas import Stage5Output, TestResult

# 创建模拟的评估结果
mock_evaluation_results = {
    "test_results": [
        {
            "scenario_id": "test_1",
            "success": False,
            "errors": ["Agent[order_agent] 处理订单失败", "超时错误"],
            "execution_time": 5.2,
            "metadata": {}
        },
        {
            "scenario_id": "test_2",
            "success": False,
            "errors": ["Agent[order_agent] 数据验证失败"],
            "execution_time": 3.1,
            "metadata": {}
        },
        {
            "scenario_id": "test_3",
            "success": False,
            "errors": ["Agent[order_agent] 权限不足"],
            "execution_time": 2.8,
            "metadata": {}
        },
        {
            "scenario_id": "test_4",
            "success": True,
            "errors": [],
            "execution_time": 1.5,
            "metadata": {}
        }
    ],
    "summary": {
        "total_tests": 4,
        "passed": 1,
        "failed": 3,
        "success_rate": 0.25
    },
    "metadata": {
        "stage": "evaluation",
        "version": "1.0.0"
    }
}

# 优化配置
optimization_config = {
    "max_iterations": 3,  # 快速测试，只迭代3次
    "num_candidates": 2,
    "top_k": 1,
    "early_stop_threshold": 0.90,
    "auto_augment_data": False,  # 快速测试，不增强数据
    "fast_mode": True  # 启用快速模式
}

def test_optimization_adapter():
    """测试优化适配器"""
    print("=" * 70)
    print("测试 OptimizationAdapter 直接调用功能")
    print("=" * 70)
    
    # 创建适配器
    adapter = OptimizationAdapter()
    
    # 验证输入
    print("\n1. 验证输入数据...")
    is_valid = adapter.validate_input(mock_evaluation_results)
    print(f"   输入验证: {'✓ 通过' if is_valid else '✗ 失败'}")
    
    # 获取元数据
    print("\n2. 获取适配器元数据...")
    metadata = adapter.get_metadata()
    print(f"   名称: {metadata['name']}")
    print(f"   版本: {metadata['version']}")
    print(f"   方法: {metadata['method']}")
    
    # 执行优化
    print("\n3. 执行优化...")
    try:
        result = adapter.process(mock_evaluation_results, optimization_config)
        
        print("\n" + "=" * 70)
        print("优化结果")
        print("=" * 70)
        print(f"优化建议数量: {len(result.suggestions)}")
        print(f"优化的 Agent 数量: {len(result.optimized_prompts)}")
        print(f"是否需要重新构建: {result.should_rebuild}")
        
        if result.suggestions:
            print("\n优化建议:")
            for i, suggestion in enumerate(result.suggestions, 1):
                print(f"\n  {i}. 目标: {suggestion.target}")
                print(f"     问题: {suggestion.issue}")
                print(f"     建议: {suggestion.suggestion}")
                print(f"     优先级: {suggestion.priority}")
                print(f"     预估影响: {suggestion.estimated_impact:.2%}")
        
        if result.optimized_prompts:
            print("\n优化后的 Prompts:")
            for agent_id, prompt in result.optimized_prompts.items():
                print(f"\n  Agent: {agent_id}")
                print(f"  Prompt: {prompt[:200]}...")
        
        print("\n性能改进:")
        for key, value in result.performance_improvement.items():
            print(f"  {key}: {value}")
        
        print("\n✓ 测试成功!")
        
    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_optimization_adapter()
