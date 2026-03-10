"""
语义对齐器 (Semantic Aligner)

这是核心模块，使用LLM进行深度语义分析：
- 判断表与实体的归属关系
- 为字段打上业务角色标签
- 推导隐藏的计算逻辑和枚举含义
"""

from typing import Dict, List, Any, Optional
import json
from openai import OpenAI


class SemanticAligner:
    """基于LLM的语义对齐器"""

    def __init__(self, api_key: str, base_url: Optional[str] = None, model: str = "gpt-4o"):
        """
        初始化语义对齐器

        Args:
            api_key: OpenAI API密钥
            base_url: API基础URL（用于兼容其他OpenAI格式的服务）
            model: 使用的模型名称
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    def analyze_table_to_entity(
        self,
        table_profile: Dict[str, Any],
        entity_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        分析表与实体的对齐关系

        Args:
            table_profile: 表的完整Profile（来自MetadataProfiler）
            entity_info: 实体信息，包含name, description, api_fields等

        Returns:
            {
                'relation_score': int (0-100),
                'relation_type': str ('core'|'association'|'log'|'irrelevant'),
                'columns_role': {
                    'business': [字段名],  # 与API直接对应
                    'technical': [字段名],  # ID、序号、时间戳
                    'hidden_logic': [字段名]  # is_deleted等必须过滤的
                },
                'field_mapping': {字段名: API字段名},
                'join_strategy': str,
                'enum_inference': {字段名: {值: 含义}},
                'reasoning': str
            }
        """
        prompt = self._build_analysis_prompt(table_profile, entity_info)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            return result

        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            return self._get_fallback_result()

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个数据库与业务建模专家。你的任务是分析数据库表与业务实体的语义关系。

**核心规则：**

1. **技术字段识别规则**：
   - 包含 ID, SN, PK, _id, _no 等后缀的字段，如果API中不存在，标记为 `technical`
   - 这些字段仅用于 JOIN 或 COUNT(DISTINCT)，不直接暴露给用户
   - created_at, updated_at, create_time 等时间戳字段也属于 technical

2. **隐藏逻辑字段识别**：
   - is_deleted, deleted, del_flag: 逻辑删除标记
   - status, state: 如果控制数据可见性，属于 hidden_logic
   - tenant_id, org_id: 多租户隔离字段
   - 这些字段在SQL中必须出现在WHERE条件中

3. **业务字段识别**：
   - 与API字段名称相似或语义相同的字段
   - 用户关心的实际业务属性（姓名、金额、数量等）

4. **关系类型判定**：
   - core: 该表是实体的主表，包含核心属性
   - association: 关联表，用于多对多关系
   - log: 流水表、日志表
   - irrelevant: 与该实体无关

5. **枚举推断**：
   - 如果采样数据中有 0/1, 1/2/3 等数字，结合字段名和注释推断含义
   - 例如：status=0可能是"禁用"，status=1可能是"启用"

**输出格式（必须是有效的JSON）**：
{
  "relation_score": 85,
  "relation_type": "core",
  "columns_role": {
    "business": ["user_name", "phone", "email"],
    "technical": ["user_id", "dept_id", "created_at"],
    "hidden_logic": ["is_deleted", "status"]
  },
  "field_mapping": {
    "user_name": "name",
    "phone": "phoneNumber"
  },
  "join_strategy": "通过 user_id 关联到部门表",
  "enum_inference": {
    "status": {"0": "禁用", "1": "启用"},
    "gender": {"1": "男", "2": "女"}
  },
  "reasoning": "该表是用户实体的核心表，包含用户基本信息..."
}
"""

    def _build_analysis_prompt(
        self,
        table_profile: Dict[str, Any],
        entity_info: Dict[str, Any]
    ) -> str:
        """构建分析提示词"""
        ddl = table_profile['ddl']
        samples = table_profile['samples']
        stats = table_profile['stats']

        # 格式化DDL信息
        ddl_text = f"表名: {ddl['table_name']}\n"
        if ddl['comment']:
            ddl_text += f"表注释: {ddl['comment']}\n"

        ddl_text += "\n字段列表:\n"
        for col in ddl['columns']:
            ddl_text += f"  - {col['name']} ({col['type']})"
            if not col['nullable']:
                ddl_text += " NOT NULL"
            if col['comment']:
                ddl_text += f" -- {col['comment']}"
            ddl_text += "\n"

        if ddl['primary_keys']:
            ddl_text += f"\n主键: {', '.join(ddl['primary_keys'])}\n"

        if ddl['foreign_keys']:
            ddl_text += "\n外键:\n"
            for fk in ddl['foreign_keys']:
                ddl_text += f"  - {fk['column']} -> {fk['ref_table']}.{fk['ref_column']}\n"

        # 格式化采样数据
        sample_text = json.dumps(samples, indent=2, ensure_ascii=False, default=str)

        # 格式化实体信息
        entity_text = f"实体名称: {entity_info.get('name', 'Unknown')}\n"
        entity_text += f"实体描述: {entity_info.get('description', '')}\n"

        if 'api_fields' in entity_info:
            entity_text += "\nAPI字段列表:\n"
            for field in entity_info['api_fields']:
                entity_text += f"  - {field.get('name', '')}"
                if field.get('description'):
                    entity_text += f": {field['description']}"
                entity_text += "\n"

        prompt = f"""请分析以下数据库表与业务实体的关系：

【业务实体信息】
{entity_text}

【数据库表DDL】
{ddl_text}

【数据采样】（共{stats['row_count']}行数据，以下是前3行）
{sample_text}

请按照系统提示中的规则，输出JSON格式的分析结果。
"""
        return prompt

    def _get_fallback_result(self) -> Dict[str, Any]:
        """LLM调用失败时的降级结果"""
        return {
            'relation_score': 0,
            'relation_type': 'irrelevant',
            'columns_role': {
                'business': [],
                'technical': [],
                'hidden_logic': []
            },
            'field_mapping': {},
            'join_strategy': '',
            'enum_inference': {},
            'reasoning': 'LLM分析失败，使用降级结果'
        }

    def batch_analyze(
        self,
        table_profiles: Dict[str, Dict[str, Any]],
        entity_info: Dict[str, Any],
        top_k: int = 10
    ) -> Dict[str, Dict[str, Any]]:
        """
        批量分析多张表与实体的关系

        Args:
            table_profiles: 所有表的Profile字典
            entity_info: 实体信息
            top_k: 只分析得分最高的前K张表

        Returns:
            {表名: 分析结果}
        """
        results = {}

        for table_name, profile in table_profiles.items():
            print(f"Analyzing {table_name} for entity {entity_info.get('name', 'Unknown')}")
            result = self.analyze_table_to_entity(profile, entity_info)
            results[table_name] = result

        # 按得分排序，只保留top_k
        sorted_results = dict(
            sorted(results.items(), key=lambda x: x[1]['relation_score'], reverse=True)[:top_k]
        )

        return sorted_results
