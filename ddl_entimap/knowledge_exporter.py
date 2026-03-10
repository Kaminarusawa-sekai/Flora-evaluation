"""
知识固化器 (Knowledge Exporter)

将LLM分析结果转化为可消费的格式：
- 生成Markdown文档（用于Vanna的Documentation）
- 生成Golden SQL样板（用于Vanna的训练）
- 导出结构化JSON（用于其他系统集成）
"""

from typing import Dict, List, Any
import json
from pathlib import Path


class KnowledgeExporter:
    """知识导出器"""

    def __init__(self, output_dir: str = "./output"):
        """
        初始化导出器

        Args:
            output_dir: 输出目录
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_entity_mapping(
        self,
        entity_name: str,
        alignment_results: Dict[str, Dict[str, Any]],
        output_format: str = "all"
    ):
        """
        导出实体映射结果

        Args:
            entity_name: 实体名称
            alignment_results: 对齐结果（来自SemanticAligner）
            output_format: 'json' | 'markdown' | 'all'
        """
        if output_format in ['json', 'all']:
            self._export_json(entity_name, alignment_results)

        if output_format in ['markdown', 'all']:
            self._export_markdown(entity_name, alignment_results)

    def _export_json(self, entity_name: str, results: Dict[str, Dict[str, Any]]):
        """导出为JSON格式"""
        output_path = self.output_dir / f"{entity_name}_mapping.json"

        export_data = {
            'entity_name': entity_name,
            'tables': results,
            'summary': self._generate_summary(results)
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        print(f"Exported JSON to {output_path}")

    def _export_markdown(self, entity_name: str, results: Dict[str, Dict[str, Any]]):
        """导出为Markdown文档"""
        output_path = self.output_dir / f"{entity_name}_mapping.md"

        md_content = self._generate_markdown(entity_name, results)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"Exported Markdown to {output_path}")

    def _generate_summary(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """生成摘要统计"""
        total_tables = len(results)
        core_tables = sum(1 for r in results.values() if r['relation_type'] == 'core')
        association_tables = sum(1 for r in results.values() if r['relation_type'] == 'association')

        total_business_fields = sum(
            len(r['columns_role']['business']) for r in results.values()
        )
        total_hidden_logic = sum(
            len(r['columns_role']['hidden_logic']) for r in results.values()
        )

        return {
            'total_tables': total_tables,
            'core_tables': core_tables,
            'association_tables': association_tables,
            'total_business_fields': total_business_fields,
            'total_hidden_logic_fields': total_hidden_logic
        }

    def _generate_markdown(self, entity_name: str, results: Dict[str, Dict[str, Any]]) -> str:
        """生成Markdown文档"""
        md = f"# {entity_name} 实体映射文档\n\n"
        md += "本文档由 EntiMap 自动生成，描述了业务实体与数据库表的映射关系。\n\n"

        # 摘要
        summary = self._generate_summary(results)
        md += "## 摘要\n\n"
        md += f"- 相关表数量: {summary['total_tables']}\n"
        md += f"- 核心表: {summary['core_tables']}\n"
        md += f"- 关联表: {summary['association_tables']}\n"
        md += f"- 业务字段总数: {summary['total_business_fields']}\n"
        md += f"- 隐藏逻辑字段: {summary['total_hidden_logic_fields']}\n\n"

        # 核心表详情
        md += "## 核心表映射\n\n"
        for table_name, result in results.items():
            if result['relation_type'] != 'core':
                continue

            md += f"### {table_name}\n\n"
            md += f"**匹配度**: {result['relation_score']}/100\n\n"
            md += f"**推理说明**: {result['reasoning']}\n\n"

            # 业务字段
            if result['columns_role']['business']:
                md += "**业务字段**:\n"
                for field in result['columns_role']['business']:
                    mapped = result['field_mapping'].get(field, '')
                    if mapped:
                        md += f"- `{field}` → API字段: `{mapped}`\n"
                    else:
                        md += f"- `{field}`\n"
                md += "\n"

            # 技术字段
            if result['columns_role']['technical']:
                md += "**技术字段** (仅用于JOIN，不暴露给用户):\n"
                for field in result['columns_role']['technical']:
                    md += f"- `{field}`\n"
                md += "\n"

            # 隐藏逻辑
            if result['columns_role']['hidden_logic']:
                md += "**隐藏逻辑字段** (SQL中必须过滤):\n"
                for field in result['columns_role']['hidden_logic']:
                    md += f"- `{field}`"
                    if field in result['enum_inference']:
                        md += f" - 枚举值: {result['enum_inference'][field]}"
                    md += "\n"
                md += "\n"

            # JOIN策略
            if result['join_strategy']:
                md += f"**关联策略**: {result['join_strategy']}\n\n"

            md += "---\n\n"

        # 关联表
        association_tables = {k: v for k, v in results.items() if v['relation_type'] == 'association'}
        if association_tables:
            md += "## 关联表\n\n"
            for table_name, result in association_tables.items():
                md += f"### {table_name}\n\n"
                md += f"**关联策略**: {result['join_strategy']}\n\n"

        # 查询注意事项
        md += "## SQL查询注意事项\n\n"
        md += "### 必须包含的过滤条件\n\n"

        hidden_logic_summary = {}
        for table_name, result in results.items():
            for field in result['columns_role']['hidden_logic']:
                if field not in hidden_logic_summary:
                    hidden_logic_summary[field] = []
                hidden_logic_summary[field].append(table_name)

        if hidden_logic_summary:
            for field, tables in hidden_logic_summary.items():
                md += f"- `{field}`: 在表 {', '.join(tables)} 中必须过滤\n"
            md += "\n"

        md += "### 枚举值说明\n\n"
        for table_name, result in results.items():
            if result['enum_inference']:
                md += f"**{table_name}**:\n"
                for field, enum_map in result['enum_inference'].items():
                    md += f"- `{field}`: {enum_map}\n"
                md += "\n"

        return md

    def generate_golden_sql(
        self,
        entity_name: str,
        alignment_results: Dict[str, Dict[str, Any]],
        sample_queries: List[str]
    ) -> List[Dict[str, str]]:
        """
        生成Golden SQL样板

        Args:
            entity_name: 实体名称
            alignment_results: 对齐结果
            sample_queries: 示例查询列表（自然语言）

        Returns:
            [{'question': str, 'sql': str}]
        """
        # 找到核心表
        core_table = None
        core_result = None
        for table_name, result in alignment_results.items():
            if result['relation_type'] == 'core':
                core_table = table_name
                core_result = result
                break

        if not core_table:
            print("Warning: No core table found, cannot generate SQL")
            return []

        golden_sqls = []

        # 生成基础查询模板
        business_fields = core_result['columns_role']['business']
        hidden_logic = core_result['columns_role']['hidden_logic']

        # 示例1: 查询所有记录
        sql = f"SELECT {', '.join(business_fields)} FROM {core_table}"
        if hidden_logic:
            conditions = []
            for field in hidden_logic:
                if 'delete' in field.lower():
                    conditions.append(f"{field} = 0")
                elif field in core_result['enum_inference']:
                    # 假设取第一个有效值
                    valid_values = [k for k in core_result['enum_inference'][field].keys() if k != '0']
                    if valid_values:
                        conditions.append(f"{field} IN ({', '.join(valid_values)})")
            if conditions:
                sql += " WHERE " + " AND ".join(conditions)

        golden_sqls.append({
            'question': f"查询所有{entity_name}",
            'sql': sql
        })

        # 示例2: 带条件查询
        if business_fields:
            first_field = business_fields[0]
            sql = f"SELECT * FROM {core_table} WHERE {first_field} LIKE '%keyword%'"
            if hidden_logic:
                sql += " AND " + " AND ".join([f"{f} = 0" if 'delete' in f.lower() else f"{f} = 1" for f in hidden_logic])

            golden_sqls.append({
                'question': f"根据{first_field}搜索{entity_name}",
                'sql': sql
            })

        # 导出到文件
        output_path = self.output_dir / f"{entity_name}_golden_sql.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(golden_sqls, f, indent=2, ensure_ascii=False)

        print(f"Generated {len(golden_sqls)} golden SQLs, saved to {output_path}")
        return golden_sqls

    def export_vanna_training_data(
        self,
        entity_name: str,
        alignment_results: Dict[str, Dict[str, Any]]
    ):
        """
        导出Vanna训练数据格式

        生成两个文件：
        1. documentation.md - 用于vanna.train(documentation=...)
        2. ddl.sql - 用于vanna.train(ddl=...)
        """
        # 生成文档
        doc_content = self._generate_markdown(entity_name, alignment_results)
        doc_path = self.output_dir / f"{entity_name}_vanna_doc.md"
        with open(doc_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        # 生成DDL（简化版，只包含相关表）
        ddl_content = f"-- {entity_name} 相关表结构\n\n"
        for table_name, result in alignment_results.items():
            if result['relation_type'] in ['core', 'association']:
                ddl_content += f"-- {table_name} (匹配度: {result['relation_score']})\n"
                ddl_content += f"-- {result['reasoning']}\n\n"

        ddl_path = self.output_dir / f"{entity_name}_vanna_ddl.sql"
        with open(ddl_path, 'w', encoding='utf-8') as f:
            f.write(ddl_content)

        print(f"Exported Vanna training data:")
        print(f"  - Documentation: {doc_path}")
        print(f"  - DDL: {ddl_path}")
