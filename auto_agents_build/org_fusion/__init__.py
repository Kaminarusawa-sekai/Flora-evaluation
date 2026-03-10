"""
Layer 3: 组织融合层 - 基于组合模式
将职能角色组织成层级化的 Agent 体系
"""

from .capability_unit_registry import CapabilityUnitRegistry
from .agent_encapsulator import AgentEncapsulator
from .capability_composer import CapabilityComposer
from .capability_promoter import CapabilityPromoter
from .topology_builder import TopologyBuilder
from .supervisor_synthesizer import SupervisorSynthesizer
from .capability_access_controller import CapabilityAccessController
from .org_blueprint_generator import OrgBlueprintGenerator

__all__ = [
    'CapabilityUnitRegistry',
    'AgentEncapsulator',
    'CapabilityComposer',
    'CapabilityPromoter',
    'TopologyBuilder',
    'SupervisorSynthesizer',
    'CapabilityAccessController',
    'OrgBlueprintGenerator'
]
