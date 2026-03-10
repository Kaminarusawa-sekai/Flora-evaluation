"""
特征提取器 (Metadata Profiler)

负责从数据库中提取结构化元数据，包括：
- 表结构（列名、类型、注释、约束）
- 数据采样（用于LLM理解实际数据含义）
- 统计信息（帮助判断表的重要性）
"""

import sqlalchemy
from sqlalchemy import inspect, text
from typing import Dict, List, Any, Optional
import json


class MetadataProfiler:
    """数据库元数据提取器"""

    def __init__(self, db_url: str):
        """
        初始化元数据提取器

        Args:
            db_url: 数据库连接字符串，如 'mysql://user:pass@host:port/db'
        """
        self.engine = sqlalchemy.create_engine(db_url)
        self.inspector = None  # 延迟初始化
        self._db_url = db_url

    def _ensure_inspector(self):
        """确保inspector已初始化"""
        if self.inspector is None:
            self.inspector = inspect(self.engine)

    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        self._ensure_inspector()
        return self.inspector.get_table_names()

    def get_table_ddl(self, table_name: str) -> Dict[str, Any]:
        """
        提取表的DDL信息

        Returns:
            {
                'table_name': str,
                'columns': [{'name', 'type', 'nullable', 'comment', 'default'}],
                'primary_keys': [str],
                'foreign_keys': [{'column', 'ref_table', 'ref_column'}],
                'indexes': [{'name', 'columns'}],
                'comment': str
            }
        """
        self._ensure_inspector()
        columns = []
        for col in self.inspector.get_columns(table_name):
            columns.append({
                'name': col['name'],
                'type': str(col['type']),
                'nullable': col['nullable'],
                'comment': col.get('comment', ''),
                'default': str(col.get('default', ''))
            })

        # 主键
        pk_constraint = self.inspector.get_pk_constraint(table_name)
        primary_keys = pk_constraint.get('constrained_columns', [])

        # 外键
        foreign_keys = []
        for fk in self.inspector.get_foreign_keys(table_name):
            foreign_keys.append({
                'column': fk['constrained_columns'][0] if fk['constrained_columns'] else None,
                'ref_table': fk['referred_table'],
                'ref_column': fk['referred_columns'][0] if fk['referred_columns'] else None
            })

        # 索引
        indexes = []
        for idx in self.inspector.get_indexes(table_name):
            indexes.append({
                'name': idx['name'],
                'columns': idx['column_names']
            })

        # 表注释（部分数据库支持）
        table_comment = ''
        try:
            table_comment = self.inspector.get_table_comment(table_name).get('text', '')
        except:
            pass

        return {
            'table_name': table_name,
            'columns': columns,
            'primary_keys': primary_keys,
            'foreign_keys': foreign_keys,
            'indexes': indexes,
            'comment': table_comment
        }

    def get_table_sample(self, table_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        获取表的采样数据

        Args:
            table_name: 表名
            limit: 采样行数，默认3行

        Returns:
            采样数据列表，每行是一个字典
        """
        try:
            with self.engine.connect() as conn:
                query = text(f"SELECT * FROM {table_name} LIMIT :limit")
                result = conn.execute(query, {"limit": limit})

                # 转换为字典列表
                columns = result.keys()
                samples = []
                for row in result:
                    samples.append(dict(zip(columns, row)))

                return samples
        except Exception as e:
            print(f"Warning: Failed to sample table {table_name}: {e}")
            return []

    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """
        获取表的统计信息

        Returns:
            {
                'row_count': int,
                'column_count': int,
                'has_data': bool
            }
        """
        try:
            with self.engine.connect() as conn:
                # 获取行数
                count_query = text(f"SELECT COUNT(*) as cnt FROM {table_name}")
                result = conn.execute(count_query)
                row_count = result.fetchone()[0]

                # 列数
                columns = self.inspector.get_columns(table_name)
                column_count = len(columns)

                return {
                    'row_count': row_count,
                    'column_count': column_count,
                    'has_data': row_count > 0
                }
        except Exception as e:
            print(f"Warning: Failed to get stats for {table_name}: {e}")
            return {
                'row_count': 0,
                'column_count': 0,
                'has_data': False
            }

    def profile_table(self, table_name: str) -> Dict[str, Any]:
        """
        完整提取一张表的所有特征

        Returns:
            包含DDL、采样数据、统计信息的完整Profile
        """
        return {
            'ddl': self.get_table_ddl(table_name),
            'samples': self.get_table_sample(table_name),
            'stats': self.get_table_stats(table_name)
        }

    def profile_all_tables(self) -> Dict[str, Dict[str, Any]]:
        """提取所有表的特征"""
        tables = self.get_all_tables()
        profiles = {}

        for table in tables:
            print(f"Profiling table: {table}")
            profiles[table] = self.profile_table(table)

        return profiles

    def export_to_json(self, output_path: str):
        """将所有表的Profile导出为JSON"""
        profiles = self.profile_all_tables()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2, ensure_ascii=False, default=str)
        print(f"Exported profiles to {output_path}")
