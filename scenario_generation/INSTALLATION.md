# 使用真实拓扑数据 - 安装指南

## 前置要求

### 1. 安装 Python 依赖

使用 pip：
```bash
pip install neo4j openai
```

或使用 conda（推荐）：
```bash
conda activate flora
conda install -c conda-forge neo4j-python-driver
pip install openai
```

### 2. 启动 Neo4j 数据库

#### 方法 1: 使用 Docker（推荐）

```bash
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/12345678 \
  neo4j:latest
```

访问 http://localhost:7474 验证 Neo4j 是否运行。

#### 方法 2: 本地安装

1. 下载 Neo4j Desktop: https://neo4j.com/download/
2. 创建数据库并启动
3. 记录连接信息（URI, 用户名, 密码）

### 3. 准备 Swagger 文件

将 `erp-server.json` 放在项目根目录：
```
Flora-evaluation/
├── erp-server.json          # Swagger 文件
├── api_normalization/
├── api_topology/
└── scenario_generation/
```

## 配置

### 修改 Neo4j 连接信息

编辑 `example_with_topology.py` 中的连接配置：

```python
topology_service = TopologyService(
    neo4j_uri="bolt://localhost:7687",      # 修改为你的 Neo4j 地址
    neo4j_user="neo4j",                     # 修改为你的用户名
    neo4j_password="12345678",              # 修改为你的密码
    llm_client=None,
    use_entity_inference=True
)
```

### 配置 LLM（可选）

如果要使用 LLM 生成更智能的测试主题：

```python
from openai import OpenAI

# OpenAI
llm_client = OpenAI(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"
)

# 通义千问
llm_client = OpenAI(
    api_key="sk-xxx",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
)

# DeepSeek
llm_client = OpenAI(
    api_key="sk-xxx",
    base_url="https://api.deepseek.com"
)

# 使用 LLM
path_generator = PathGenerator(llm_client=llm_client)
```

## 运行

### 方法 1: 自动运行（推荐）

```bash
cd scenario_generation
python run_real_topology_auto.py
```

### 方法 2: 交互式运行

```bash
cd scenario_generation
python run_with_real_topology.py
```

### 方法 3: 在代码中调用

```python
from scenario_generation.example_with_topology import example_with_real_topology

example_with_real_topology()
```

## 验证安装

运行以下命令验证依赖是否正确安装：

```bash
python -c "import neo4j; print('neo4j:', neo4j.__version__)"
python -c "from api_normalization import NormalizationService; print('api_normalization: OK')"
python -c "from api_topology import TopologyService; print('api_topology: OK')"
```

## 故障排除

### 问题 1: ModuleNotFoundError: No module named 'neo4j'

**解决方案：**
```bash
pip install neo4j
# 或
conda install -c conda-forge neo4j-python-driver
```

### 问题 2: Neo4j 连接失败

**检查：**
1. Neo4j 是否运行：`docker ps | grep neo4j`
2. 端口是否正确：默认 7687
3. 用户名密码是否正确

**解决方案：**
```bash
# 重启 Neo4j
docker restart neo4j

# 查看日志
docker logs neo4j
```

### 问题 3: erp-server.json not found

**解决方案：**
确保文件在正确位置：
```bash
ls E:/Data/Flora-evaluation/erp-server.json
```

### 问题 4: 'NoneType' object is not iterable

这个问题已经修复。如果仍然出现，请确保：
1. 使用最新版本的 `path_generator.py`
2. Neo4j 中的数据格式正确

### 问题 5: LLM API 调用失败

**解决方案：**
- 检查 API key 是否正确
- 检查网络连接
- 系统会自动降级到启发式方法，不影响功能

## 输出

成功运行后，会生成：

```
scenario_generation/output/real_topology_scenarios.json
```

包含：
- 拓扑摘要（APIs, dependencies, entities）
- 发现的路径列表
- 生成的测试场景
- 统计信息

## 示例输出

```json
{
  "metadata": {
    "source_file": "erp-server.json",
    "total_apis": 150,
    "total_dependencies": 320,
    "total_entities": 25
  },
  "paths": [
    {
      "path": ["login", "createOrder", "getOrder"],
      "test_objective": "测试用户创建订单流程",
      "description": "验证用户登录后创建订单并查询订单详情"
    }
  ],
  "scenarios": [...],
  "statistics": {
    "total_paths": 10,
    "total_scenarios": 20,
    "valid_scenarios": 20,
    "average_score": 0.95
  }
}
```

## 下一步

1. 查看生成的场景：`cat output/real_topology_scenarios.json`
2. 分析路径质量
3. 调整参数重新生成
4. 使用 LLM 提高主题质量

## 联系支持

如果遇到问题，请检查：
1. Python 版本：3.8+
2. 依赖版本：`pip list | grep neo4j`
3. Neo4j 版本：4.0+
