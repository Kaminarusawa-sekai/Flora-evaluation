"""
测试 Neo4j 连接和数据库访问
"""
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_neo4j_connection():
    """测试 Neo4j 连接"""
    uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    
    print(f"Testing connection to: {uri}")
    print(f"User: {user}")
    
    try:
        driver = GraphDatabase.driver(uri, auth=(user, password))
        
        # 测试连接
        driver.verify_connectivity()
        print("✓ Connection successful!")
        
        # 列出所有数据库
        with driver.session(database="system") as session:
            result = session.run("SHOW DATABASES")
            databases = [record["name"] for record in result]
            print(f"\n✓ Available databases: {databases}")
        
        # 测试默认数据库
        database = "neo4j"
        print(f"\n✓ Testing database: {database}")
        
        with driver.session(database=database) as session:
            # 检查是否有 API 节点
            result = session.run("MATCH (a:API) RETURN count(a) as count")
            api_count = result.single()["count"]
            print(f"  - API nodes: {api_count}")
            
            # 检查是否有 Entity 节点
            result = session.run("MATCH (e:Entity) RETURN count(e) as count")
            entity_count = result.single()["count"]
            print(f"  - Entity nodes: {entity_count}")
            
            # 检查是否有依赖关系
            result = session.run("MATCH ()-[r:DEPENDS_ON]->() RETURN count(r) as count")
            dep_count = result.single()["count"]
            print(f"  - DEPENDS_ON relationships: {dep_count}")
            
            if api_count == 0:
                print("\n⚠ Warning: No API nodes found in database!")
                print("  You may need to run the topology stage first to populate the database.")
            else:
                print(f"\n✓ Database contains topology data!")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = test_neo4j_connection()
    exit(0 if success else 1)
