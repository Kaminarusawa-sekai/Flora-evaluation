"""
EntiMap 单元测试

测试核心功能模块
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import json
from ddl_entimap import MetadataProfiler, SemanticAligner, KnowledgeExporter, EntiMapEngine


class TestMetadataProfiler(unittest.TestCase):
    """测试元数据提取器"""

    @patch('ddl_entimap.metadata_profiler.sqlalchemy.create_engine')
    def test_get_all_tables(self, mock_create_engine):
        """测试获取所有表名"""
        mock_inspector = Mock()
        mock_inspector.get_table_names.return_value = ['user', 'order', 'product']

        with patch('ddl_entimap.metadata_profiler.inspect', return_value=mock_inspector):
            profiler = MetadataProfiler("sqlite:///:memory:")
            tables = profiler.get_all_tables()

            self.assertEqual(len(tables), 3)
            self.assertIn('user', tables)

    @patch('ddl_entimap.metadata_profiler.sqlalchemy.create_engine')
    def test_get_table_ddl(self, mock_create_engine):
        """测试提取表DDL"""
        mock_inspector = Mock()
        mock_inspector.get_columns.return_value = [
            {
                'name': 'id',
                'type': 'INTEGER',
                'nullable': False,
                'comment': '主键',
                'default': None
            },
            {
                'name': 'name',
                'type': 'VARCHAR(100)',
                'nullable': True,
                'comment': '用户名',
                'default': None
            }
        ]
        mock_inspector.get_pk_constraint.return_value = {'constrained_columns': ['id']}
        mock_inspector.get_foreign_keys.return_value = []
        mock_inspector.get_indexes.return_value = []
        mock_inspector.get_table_comment.return_value = {'text': '用户表'}

        with patch('ddl_entimap.metadata_profiler.inspect', return_value=mock_inspector):
            profiler = MetadataProfiler("sqlite:///:memory:")
            ddl = profiler.get_table_ddl('user')

            self.assertEqual(ddl['table_name'], 'user')
            self.assertEqual(len(ddl['columns']), 2)
            self.assertEqual(ddl['primary_keys'], ['id'])
            self.assertEqual(ddl['comment'], '用户表')


class TestSemanticAligner(unittest.TestCase):
    """测试语义对齐器"""

    def test_system_prompt(self):
        """测试系统提示词包含关键规则"""
        aligner = SemanticAligner(api_key="test-key")
        system_prompt = aligner._get_system_prompt()

        # 检查关键规则是否存在
        self.assertIn('technical', system_prompt)
        self.assertIn('hidden_logic', system_prompt)
        self.assertIn('business', system_prompt)
        self.assertIn('is_deleted', system_prompt)

    @patch('ddl_entimap.semantic_aligner.OpenAI')
    def test_analyze_table_to_entity(self, mock_openai):
        """测试表与实体对齐分析"""
        # Mock LLM响应
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            'relation_score': 85,
            'relation_type': 'core',
            'columns_role': {
                'business': ['user_name', 'phone'],
                'technical': ['user_id'],
                'hidden_logic': ['is_deleted']
            },
            'field_mapping': {'user_name': 'userName'},
            'join_strategy': '主表',
            'enum_inference': {},
            'reasoning': '这是用户核心表'
        })

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client

        aligner = SemanticAligner(api_key="test-key")

        table_profile = {
            'ddl': {
                'table_name': 'sys_user',
                'columns': [
                    {'name': 'user_id', 'type': 'INT', 'nullable': False, 'comment': '', 'default': ''},
                    {'name': 'user_name', 'type': 'VARCHAR', 'nullable': True, 'comment': '用户名', 'default': ''}
                ],
                'primary_keys': ['user_id'],
                'foreign_keys': [],
                'indexes': [],
                'comment': '用户表'
            },
            'samples': [{'user_id': 1, 'user_name': 'test'}],
            'stats': {'row_count': 100, 'column_count': 2, 'has_data': True}
        }

        entity_info = {
            'name': 'User',
            'description': '用户实体',
            'api_fields': [{'name': 'userName', 'description': '用户名'}]
        }

        result = aligner.analyze_table_to_entity(table_profile, entity_info)

        self.assertEqual(result['relation_score'], 85)
        self.assertEqual(result['relation_type'], 'core')
        self.assertIn('user_name', result['columns_role']['business'])


class TestKnowledgeExporter(unittest.TestCase):
    """测试知识导出器"""

    def test_generate_summary(self):
        """测试生成摘要统计"""
        exporter = KnowledgeExporter(output_dir="./test_output")

        results = {
            'table1': {
                'relation_type': 'core',
                'columns_role': {
                    'business': ['field1', 'field2'],
                    'technical': ['id'],
                    'hidden_logic': ['is_deleted']
                }
            },
            'table2': {
                'relation_type': 'association',
                'columns_role': {
                    'business': ['field3'],
                    'technical': [],
                    'hidden_logic': []
                }
            }
        }

        summary = exporter._generate_summary(results)

        self.assertEqual(summary['total_tables'], 2)
        self.assertEqual(summary['core_tables'], 1)
        self.assertEqual(summary['association_tables'], 1)
        self.assertEqual(summary['total_business_fields'], 3)
        self.assertEqual(summary['total_hidden_logic_fields'], 1)

    def test_generate_markdown(self):
        """测试生成Markdown文档"""
        exporter = KnowledgeExporter(output_dir="./test_output")

        results = {
            'sys_user': {
                'relation_score': 90,
                'relation_type': 'core',
                'columns_role': {
                    'business': ['user_name'],
                    'technical': ['user_id'],
                    'hidden_logic': ['is_deleted']
                },
                'field_mapping': {'user_name': 'userName'},
                'join_strategy': '主表',
                'enum_inference': {'is_deleted': {'0': '正常', '1': '已删除'}},
                'reasoning': '用户核心表'
            }
        }

        md = exporter._generate_markdown('User', results)

        self.assertIn('# User', md)
        self.assertIn('sys_user', md)
        self.assertIn('user_name', md)
        self.assertIn('is_deleted', md)
        self.assertIn('90/100', md)


class TestEntiMapEngine(unittest.TestCase):
    """测试EntiMap引擎"""

    @patch('ddl_entimap.entimap_engine.MetadataProfiler')
    @patch('ddl_entimap.entimap_engine.SemanticAligner')
    @patch('ddl_entimap.entimap_engine.KnowledgeExporter')
    def test_engine_initialization(self, mock_exporter, mock_aligner, mock_profiler):
        """测试引擎初始化"""
        engine = EntiMapEngine(
            db_url="sqlite:///:memory:",
            api_key="test-key",
            model="gpt-4o",
            output_dir="./output"
        )

        self.assertIsNotNone(engine.profiler)
        self.assertIsNotNone(engine.aligner)
        self.assertIsNotNone(engine.exporter)

    @patch('ddl_entimap.entimap_engine.MetadataProfiler')
    @patch('ddl_entimap.entimap_engine.SemanticAligner')
    @patch('ddl_entimap.entimap_engine.KnowledgeExporter')
    def test_get_summary(self, mock_exporter, mock_aligner, mock_profiler):
        """测试获取状态摘要"""
        engine = EntiMapEngine(
            db_url="sqlite:///:memory:",
            api_key="test-key"
        )

        # 未初始化状态
        summary = engine.get_summary()
        self.assertEqual(summary['status'], 'not_initialized')

        # 已初始化状态
        engine.table_profiles = {
            'table1': {'stats': {'has_data': True, 'column_count': 5}},
            'table2': {'stats': {'has_data': False, 'column_count': 3}}
        }

        summary = engine.get_summary()
        self.assertEqual(summary['status'], 'ready')
        self.assertEqual(summary['total_tables'], 2)
        self.assertEqual(summary['tables_with_data'], 1)
        self.assertEqual(summary['total_columns'], 8)


if __name__ == '__main__':
    unittest.main()
