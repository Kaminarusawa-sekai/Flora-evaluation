"""
Layer 2: 职能对齐层
将技术性 API 能力映射到业务性职能角色
"""

from .functional_meta_library import FunctionalMetaLibrary
from .domain_detector import DomainDetector
from .semantic_alignment_engine import SemanticAlignmentEngine
from .template_loader import TemplateLoader
from .capability_slotter import CapabilitySlotter
from .gap_analyzer import GapAnalyzer
from .constraint_injector import ConstraintInjector
from .role_manifest_generator import RoleManifestGenerator

__all__ = [
    'FunctionalMetaLibrary',
    'DomainDetector',
    'SemanticAlignmentEngine',
    'TemplateLoader',
    'CapabilitySlotter',
    'GapAnalyzer',
    'ConstraintInjector',
    'RoleManifestGenerator'
]
