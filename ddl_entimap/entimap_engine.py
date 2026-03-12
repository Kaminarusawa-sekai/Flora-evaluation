"""
EntiMap引擎 (EntiMap Engine)

这是整个方案的主入口，协调所有模块完成端到端的自动化流程：
1. 提取数据库元数据
2. 使用RAG检索相关表（可选）
3. LLM深度语义对齐
4. 导出知识产物
"""

from typing import Dict, List, Any, Optional
from .metadata_profiler import MetadataProfiler
from .semantic_aligner import SemanticAligner
from .knowledge_exporter import KnowledgeExporter
import json


class EntiMapEngine:
    """EntiMap主引擎"""

    def __init__(
        self,
        db_url: str,
        api_key: str,
        base_url: Optional[str] = None,
        model: str = "gpt-4o",
        output_dir: str = "./output"
    ):
        """
        初始化EntiMap引擎

        Args:
            db_url: 数据库连接字符串
            api_key: OpenAI API密钥
            base_url: API基础URL（用于兼容其他服务）
            model: LLM模型名称
            output_dir: 输出目录
        """
        self.profiler = MetadataProfiler(db_url)
        self.aligner = SemanticAligner(api_key, base_url, model)
        self.exporter = KnowledgeExporter(output_dir)

        self.table_profiles = None  # 缓存表的Profile

    def load_api_entities(self, entities_path: str) -> List[Dict[str, Any]]:
        """
        加载API实体定义

        Args:
            entities_path: 实体定义JSON文件路径

        Returns:
            实体列表，每个实体包含：
            {
                'name': str,
                'description': str,
                'api_fields': [{'name': str, 'description': str, 'type': str}],
                'api_paths': [str]
            }
        """
        with open(entities_path, 'r', encoding='utf-8') as f:
            entities = json.load(f)
        return entities

    def profile_database(self, cache_path: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
        """
        提取数据库所有表的元数据

        Args:
            cache_path: 如果提供，将结果缓存到该路径

        Returns:
            {表名: Profile}
        """
        print("=" * 60)
        print("Step 1: Profiling Database Metadata")
        print("=" * 60)

        self.table_profiles = self.profiler.profile_all_tables()

        if cache_path:
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.table_profiles, f, indent=2, ensure_ascii=False, default=str)
            print(f"\nCached profiles to {cache_path}")

        print(f"\nProfiled {len(self.table_profiles)} tables")
        return self.table_profiles

    def load_cached_profiles(self, cache_path: str):
        """加载缓存的表Profile"""
        with open(cache_path, 'r', encoding='utf-8') as f:
            self.table_profiles = json.load(f)
        print(f"Loaded {len(self.table_profiles)} cached table profiles")

    def align_entity(
        self,
        entity_info: Dict[str, Any],
        table_profiles: Optional[Dict[str, Dict[str, Any]]] = None,
        top_k: int = 10
    ) -> Dict[str, Dict[str, Any]]:
        """
        将单个实体与数据库表对齐

        Args:
            entity_info: 实体信息
            table_profiles: 表Profile字典（如果为None，使用缓存的）
            top_k: 只保留得分最高的前K张表

        Returns:
            {表名: 对齐结果}
        """
        if table_profiles is None:
            if self.table_profiles is None:
                self.profile_database()
                if self.table_profiles is None:
                    raise ValueError("No table profiles available. Run profile_database() first.")
            table_profiles = self.table_profiles

        print("\n" + "=" * 60)
        print(f"Step 2: Aligning Entity '{entity_info.get('name', 'Unknown')}'")
        print("=" * 60)

        # 使用LLM批量分析
        alignment_results = self.aligner.batch_analyze(
            table_profiles,
            entity_info,
            top_k=top_k
        )

        print(f"\nFound {len(alignment_results)} relevant tables")
        return alignment_results

    def export_results(
        self,
        entity_name: str,
        alignment_results: Dict[str, Dict[str, Any]],
        export_format: str = "all",
        generate_sql: bool = True
    ):
        """
        导出对齐结果

        Args:
            entity_name: 实体名称
            alignment_results: 对齐结果
            export_format: 'json' | 'markdown' | 'all'
            generate_sql: 是否生成Golden SQL
        """
        print("\n" + "=" * 60)
        print(f"Step 3: Exporting Results for '{entity_name}'")
        print("=" * 60)

        # 导出映射文档
        self.exporter.export_entity_mapping(
            entity_name,
            alignment_results,
            output_format=export_format
        )

        # 生成Golden SQL
        if generate_sql:
            self.exporter.generate_golden_sql(
                entity_name,
                alignment_results,
                sample_queries=[]
            )

        # 导出Vanna训练数据
        self.exporter.export_vanna_training_data(
            entity_name,
            alignment_results
        )

    def run_full_pipeline(
        self,
        entities_path: str,
        cache_profiles: bool = True,
        top_k_tables: int = 10
    ):
        """
        运行完整的端到端流程

        Args:
            entities_path: API实体定义文件路径
            cache_profiles: 是否缓存表Profile
            top_k_tables: 每个实体保留的最相关表数量
        """
        print("\n" + "=" * 60)
        print("EntiMap - 语义驱动的自动化建模引擎")
        print("=" * 60)

        # Step 1: 提取数据库元数据
        cache_path = "table_profiles_cache.json" if cache_profiles else None
        self.profile_database(cache_path)

        # Step 2: 加载API实体
        print("\n" + "=" * 60)
        print("Loading API Entities")
        print("=" * 60)
        entities = self.load_api_entities(entities_path)
        print(f"Loaded {len(entities)} entities")

        # Step 3: 逐个实体进行对齐
        for entity in entities:
            entity_name = entity.get('name', 'Unknown')

            try:
                # 对齐
                alignment_results = self.align_entity(
                    entity,
                    top_k=top_k_tables
                )

                # 导出
                self.export_results(
                    entity_name,
                    alignment_results,
                    export_format="all",
                    generate_sql=True
                )

            except Exception as e:
                print(f"\nError processing entity {entity_name}: {e}")
                continue

        print("\n" + "=" * 60)
        print("Pipeline Completed!")
        print("=" * 60)

    def quick_align(
        self,
        entity_name: str,
        entity_description: str,
        api_fields: List[Dict[str, str]],
        top_k: int = 5
    ) -> Dict[str, Dict[str, Any]]:
        """
        快速对齐单个实体（不需要预先准备JSON文件）

        Args:
            entity_name: 实体名称
            entity_description: 实体描述
            api_fields: API字段列表 [{'name': str, 'description': str}]
            top_k: 保留的最相关表数量

        Returns:
            对齐结果
        """
        # 确保已经提取了表Profile
        if self.table_profiles is None:
            print("Profiling database first...")
            self.profile_database()

        # 构建实体信息
        entity_info = {
            'name': entity_name,
            'description': entity_description,
            'api_fields': api_fields
        }

        # 对齐
        alignment_results = self.align_entity(entity_info, top_k=top_k)

        # 导出
        self.export_results(entity_name, alignment_results)

        return alignment_results

    def get_summary(self) -> Dict[str, Any]:
        """获取当前状态摘要"""
        if self.table_profiles is None:
            return {
                'status': 'not_initialized',
                'message': 'No table profiles loaded. Run profile_database() first.'
            }

        return {
            'status': 'ready',
            'total_tables': len(self.table_profiles),
            'tables_with_data': sum(
                1 for p in self.table_profiles.values()
                if p['stats']['has_data']
            ),
            'total_columns': sum(
                p['stats']['column_count']
                for p in self.table_profiles.values()
            )
        }
