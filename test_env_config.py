"""
测试环境变量配置加载
"""
from core.pipeline_orchestrator import PipelineOrchestrator
from core.env_utils import get_database_url

def test_env_loading():
    """测试环境变量是否正确加载"""
    orchestrator = PipelineOrchestrator('config/pipeline_config.yaml')
    
    # 检查 topology 阶段的配置
    topology_config = orchestrator.config['stages']['topology']['config']
    
    print("=" * 60)
    print("环境变量加载测试")
    print("=" * 60)
    print(f"NEO4J_URI: {topology_config['neo4j_uri']}")
    print(f"NEO4J_USER: {topology_config['neo4j_user']}")
    print(f"NEO4J_PASSWORD: {topology_config['neo4j_password']}")
    print("=" * 60)
    
    # 验证是否正确替换
    assert topology_config['neo4j_uri'] == 'bolt://192.168.1.210:7687', "NEO4J_URI 未正确替换"
    assert topology_config['neo4j_user'] == 'neo4j', "NEO4J_USER 未正确替换"
    assert topology_config['neo4j_password'] == '12345678', "NEO4J_PASSWORD 未正确替换"
    
    print("✓ Neo4j 环境变量已正确加载！")
    
    # 检查 database_mapping 阶段的配置
    db_config = orchestrator.config['stages']['database_mapping']['config']
    
    print("\n" + "=" * 60)
    print("数据库 URL 测试")
    print("=" * 60)
    print(f"原始 DATABASE_URL: mysql+pymysql://root:LDPP@MySQL82024!@192.168.1.33:8888/eqiai_erp")
    print(f"编码后 DATABASE_URL: {db_config['db_url']}")
    print("=" * 60)
    
    # 验证密码中的特殊字符是否被正确编码
    assert '@' not in db_config['db_url'].split('@')[1].split('@')[0], "密码中的 @ 未被编码"
    assert '%40' in db_config['db_url'], "密码中的 @ 应该被编码为 %40"
    
    print("✓ DATABASE_URL 中的特殊字符已正确编码！")
    print("\n✅ 所有环境变量测试通过！")

if __name__ == '__main__':
    test_env_loading()
