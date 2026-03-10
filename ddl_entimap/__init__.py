"""
EntiMap - 基于业务实体的自动化语义对齐方案

这个模块提供了一套完整的解决方案，用于将物理数据库（DDL）自动对齐到业务实体（API定义）。
通过LLM驱动的语义分析，实现从杂乱的数据库结构到清晰的业务模型的自动化映射。
"""

from .metadata_profiler import MetadataProfiler
from .semantic_aligner import SemanticAligner
from .knowledge_exporter import KnowledgeExporter
from .entimap_engine import EntiMapEngine

__all__ = [
    'MetadataProfiler',
    'SemanticAligner',
    'KnowledgeExporter',
    'EntiMapEngine'
]

__version__ = '1.0.0'
