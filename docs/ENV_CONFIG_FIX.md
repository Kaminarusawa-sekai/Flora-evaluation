# 环境变量配置修复说明

## 问题描述

在使用 `pipeline_orchestrator.py` 时，遇到以下问题：

1. YAML 配置文件中的环境变量占位符（如 `${NEO4J_URI}`）没有被替换，导致传递空字符串给服务
2. 数据库密码中包含特殊字符（如 `@`）导致 URL 解析错误

## 解决方案

### 1. 环境变量自动替换

修改了 `core/pipeline_orchestrator.py`，添加了环境变量替换功能：

- 在初始化时自动加载 `.env` 文件
- 解析 YAML 配置时自动替换 `${VAR_NAME}` 格式的占位符
- 支持所有环境变量的自动替换

### 2. 数据库密码特殊字符处理

创建了 `core/env_utils.py` 工具模块，提供以下功能：

- `get_database_url()`: 自动处理 DATABASE_URL 中密码的特殊字符编码
- `encode_db_password()`: 对密码进行 URL 编码
- `build_database_url()`: 构建完整的数据库 URL，自动编码密码

## 使用方法

### 配置 .env 文件

```bash
# Neo4j 配置
NEO4J_URI=bolt://192.168.1.210:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=12345678

# 数据库配置（密码中的特殊字符无需手动编码）
DATABASE_URL=mysql+pymysql://root:LDPP@MySQL82024!@192.168.1.33:8888/eqiai_erp
```

### YAML 配置文件

```yaml
stages:
  topology:
    config:
      neo4j_uri: "${NEO4J_URI}"
      neo4j_user: "${NEO4J_USER}"
      neo4j_password: "${NEO4J_PASSWORD}"
  
  database_mapping:
    config:
      db_url: "${DATABASE_URL}"
```

### 运行程序

```bash
python main.py
```

系统会自动：
1. 加载 `.env` 文件
2. 替换 YAML 中的环境变量占位符
3. 对 DATABASE_URL 中的密码特殊字符进行编码

## 特殊字符编码示例

| 原始密码 | 编码后 |
|---------|--------|
| `pass@word` | `pass%40word` |
| `pass!word` | `pass%21word` |
| `pass#word` | `pass%23word` |
| `LDPP@MySQL82024!` | `LDPP%40MySQL82024%21` |

## 测试

运行测试脚本验证配置：

```bash
# 测试环境变量加载
python test_env_config.py

# 演示密码编码效果
python demo_password_encoding.py
```

## 技术细节

### 环境变量替换流程

1. `PipelineOrchestrator.__init__()` 调用 `load_dotenv()` 加载环境变量
2. `_load_config()` 读取 YAML 文件内容为字符串
3. `_replace_env_vars()` 使用正则表达式查找并替换 `${VAR_NAME}` 占位符
4. 对于 `DATABASE_URL`，调用 `get_database_url()` 进行特殊处理
5. 返回解析后的配置字典

### 密码编码流程

1. `get_database_url()` 使用 `urlparse()` 解析数据库 URL
2. 提取用户名和密码
3. 使用 `quote_plus()` 对密码进行 URL 编码
4. 重新构建完整的 URL

## 依赖

- `python-dotenv`: 加载 .env 文件
- `urllib.parse`: URL 解析和编码

这些依赖已包含在 `requirements_core.txt` 中。
