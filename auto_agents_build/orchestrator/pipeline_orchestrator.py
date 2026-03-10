"""
流水线编排器 - 协调四层的执行流程
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Optional
from datetime import datetime
from shared.logger import get_logger
from shared.llm_client import LLMClient
from shared.vector_store import VectorStore
from shared.config_loader import get_config
from shared.utils import save_json, ensure_dir

# Layer 2
from role_alignment import (
    FunctionalMetaLibrary,
    DomainDetector,
    SemanticAlignmentEngine,
    TemplateLoader,
    CapabilitySlotter,
    GapAnalyzer,
    ConstraintInjector,
    RoleManifestGenerator
)

# Layer 3
from org_fusion import (
    CapabilityUnitRegistry,
    AgentEncapsulator,
    CapabilityComposer,
    CapabilityPromoter,
    TopologyBuilder,
    SupervisorSynthesizer,
    CapabilityAccessController,
    OrgBlueprintGenerator
)

# Layer 4
from artifact_generation import (
    PromptFactory,
    ManifestGenerator,
    RAGKnowledgeLinker,
    MonitoringConfigGenerator
)

logger = get_logger(__name__)


class PipelineOrchestrator:
    """流水线编排器"""

    def __init__(self, config_path: Optional[str] = None):
        self.config = get_config()
        self.llm_client = LLMClient()
        self.vector_store = VectorStore()

        # 初始化各层组件
        self._init_layer2_components()
        self._init_layer3_components()
        self._init_layer4_components()

    def _init_layer2_components(self):
        """初始化 Layer 2 组件"""
        self.meta_library = FunctionalMetaLibrary()
        self.domain_detector = DomainDetector(self.meta_library, self.llm_client)
        self.alignment_engine = SemanticAlignmentEngine(self.llm_client, self.vector_store)
        self.template_loader = TemplateLoader(self.meta_library, self.llm_client)
        self.capability_slotter = CapabilitySlotter()
        self.gap_analyzer = GapAnalyzer(self.llm_client)
        self.constraint_injector = ConstraintInjector(self.llm_client)
        self.role_manifest_generator = RoleManifestGenerator()

    def _init_layer3_components(self):
        """初始化 Layer 3 组件"""
        self.capability_registry = CapabilityUnitRegistry()
        self.agent_encapsulator = AgentEncapsulator(self.capability_registry)
        self.capability_composer = CapabilityComposer(self.capability_registry, self.llm_client)
        self.capability_promoter = CapabilityPromoter(self.capability_registry, self.llm_client)
        self.topology_builder = TopologyBuilder()
        self.supervisor_synthesizer = SupervisorSynthesizer(
            self.capability_registry,
            self.llm_client,
            self.capability_promoter
        )
        self.access_controller = CapabilityAccessController(self.capability_registry)
        self.blueprint_generator = OrgBlueprintGenerator()

    def _init_layer4_components(self):
        """初始化 Layer 4 组件"""
        self.prompt_factory = PromptFactory(self.llm_client)
        self.manifest_generator = ManifestGenerator()
        self.rag_linker = RAGKnowledgeLinker()
        self.monitoring_generator = MonitoringConfigGenerator()

    def run_pipeline(
        self,
        api_capabilities: List[Dict[str, Any]],
        output_dir: str = "./output"
    ) -> Dict[str, Any]:
        """
        运行完整流水线

        Args:
            api_capabilities: API 能力列表（来自 Layer 1）
            output_dir: 输出目录

        Returns:
            执行结果
        """
        logger.info("=" * 60)
        logger.info("Starting Agent Build Pipeline")
        logger.info("=" * 60)

        ensure_dir(output_dir)

        start_time = datetime.now()
        results = {}

        try:
            # Layer 2: 职能对齐层
            logger.info("\n[Layer 2] 职能对齐层 - 开始执行")
            layer2_result = self._execute_layer2(api_capabilities, output_dir)
            results['layer2'] = layer2_result

            # Layer 3: 组织融合层
            logger.info("\n[Layer 3] 组织融合层 - 开始执行")
            layer3_result = self._execute_layer3(layer2_result, output_dir)
            results['layer3'] = layer3_result

            # Layer 4: 代码生成层
            logger.info("\n[Layer 4] 代码生成层 - 开始执行")
            layer4_result = self._execute_layer4(layer3_result, layer2_result, output_dir)
            results['layer4'] = layer4_result

            duration = (datetime.now() - start_time).total_seconds()
            results['success'] = True
            results['duration_seconds'] = duration

            logger.info("\n" + "=" * 60)
            logger.info(f"Pipeline completed successfully in {duration:.2f}s")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            results['success'] = False
            results['error'] = str(e)

        # 保存总结果
        save_json(results, f"{output_dir}/pipeline_result.json")

        return results

    def _execute_layer2(
        self,
        api_capabilities: List[Dict[str, Any]],
        output_dir: str
    ) -> Dict[str, Any]:
        """执行 Layer 2"""
        layer2_dir = f"{output_dir}/layer2"
        ensure_dir(layer2_dir)

        # 1. 领域探测
        logger.info("  [1/7] 领域探测...")
        domain_info = self.domain_detector.detect_domains(api_capabilities)

        # 2. 加载模板
        logger.info("  [2/7] 加载角色模板...")
        roles = self.template_loader.load_templates(
            domain_info['primary_domain'],
            domain_info.get('secondary_domains', [])
        )

        # 3. 语义对齐
        logger.info("  [3/7] 语义对齐...")
        alignment_result = self.alignment_engine.align_capabilities_to_roles(
            api_capabilities,
            roles
        )

        # 4. 能力填装
        logger.info("  [4/7] 能力填装...")
        slotting_result = self.capability_slotter.slot_capabilities(roles, alignment_result)
        filled_roles = slotting_result['filled_roles']

        # 5. 差异分析
        logger.info("  [5/7] 差异分析...")
        orphan_apis = self.capability_slotter.find_orphan_apis(api_capabilities, alignment_result)
        gap_result = self.gap_analyzer.analyze_gaps(filled_roles, orphan_apis)
        adjusted_roles = gap_result['adjusted_roles']

        # 6. 约束注入
        logger.info("  [6/7] 约束注入...")
        constraint_result = self.constraint_injector.inject_constraints(adjusted_roles)
        roles_with_constraints = constraint_result['roles_with_constraints']
        contracts = constraint_result['contracts']

        # 7. 生成清单
        logger.info("  [7/7] 生成角色清单...")
        manifest = self.role_manifest_generator.generate_manifest(
            roles_with_constraints,
            domain_info,
            contracts,
            gap_result['report']
        )

        # 保存输出
        self.role_manifest_generator.save_manifest(manifest, f"{layer2_dir}/role_manifest.json")

        # 生成报告
        report = self.role_manifest_generator.generate_summary_report(manifest)
        logger.info("\n" + report)

        return manifest

    def _execute_layer3(
        self,
        layer2_result: Dict[str, Any],
        output_dir: str
    ) -> Dict[str, Any]:
        """执行 Layer 3"""
        layer3_dir = f"{output_dir}/layer3"
        ensure_dir(layer3_dir)

        roles = layer2_result['roles']
        contracts = layer2_result.get('contracts', [])

        # 1. 注册原子能力
        logger.info("  [1/7] 注册原子能力...")
        role_to_capabilities = {}
        for role in roles:
            capability_units = []
            for api in role.get('assigned_apis', []):
                unit_id = self.capability_registry.register_atomic_capability(
                    name=api['business_name'],
                    underlying_apis=[f"{api['method']} {api['path']}"],
                    required_params=[],
                    constraints=api.get('constraints', []),
                    owner=role['role_name']
                )
                capability_units.append(unit_id)
            role_to_capabilities[role['role_id']] = capability_units

        # 2. 封装 Agent
        logger.info("  [2/7] 封装 Agent...")
        agents = self.agent_encapsulator.batch_encapsulate(roles, role_to_capabilities)

        # 3. 能力组合
        logger.info("  [3/7] 能力组合...")
        self.capability_composer.compose_capabilities(agents)

        # 4. 能力晋升
        logger.info("  [4/7] 能力晋升...")
        self.capability_promoter.batch_promote(agents)

        # 5. 合成主管
        logger.info("  [5/7] 合成主管...")
        specialist_agents = [a for a in agents if a['level'] == 'specialist']
        if specialist_agents:
            supervisors = self.supervisor_synthesizer.synthesize_supervisors(specialist_agents)
            agents.extend(supervisors)

        # 6. 构建拓扑
        logger.info("  [6/7] 构建拓扑...")
        agents = self.topology_builder.infer_hierarchy(agents)
        registry_data = self.capability_registry.export_registry()
        topology = self.topology_builder.build_topology(agents, registry_data)

        # 7. 访问控制
        logger.info("  [7/7] 构建访问控制矩阵...")
        access_matrix = self.access_controller.build_access_control_matrix(agents)

        # 生成蓝图
        blueprint = self.blueprint_generator.generate_blueprint(
            agents,
            registry_data,
            topology,
            access_matrix,
            contracts
        )

        # 保存输出
        self.blueprint_generator.save_blueprint(blueprint, f"{layer3_dir}/org_blueprint.json")

        # 生成报告
        report = self.blueprint_generator.generate_summary_report(blueprint)
        logger.info("\n" + report)

        return blueprint

    def _execute_layer4(
        self,
        layer3_result: Dict[str, Any],
        layer2_result: Dict[str, Any],
        output_dir: str
    ) -> Dict[str, Any]:
        """执行 Layer 4"""
        layer4_dir = f"{output_dir}/layer4"
        ensure_dir(layer4_dir)

        agents = layer3_result['agent_definitions']
        capability_registry = layer3_result['capability_registry']
        contracts = layer2_result.get('contracts', [])
        domain = layer2_result.get('domain', 'Unknown')

        # 1. 生成 Prompt
        logger.info("  [1/4] 生成 Agent Prompt...")
        prompts = self.prompt_factory.generate_prompts(agents, capability_registry, contracts)
        self.prompt_factory.save_prompts(prompts, f"{layer4_dir}/prompts")

        # 2. 生成 Manifest
        logger.info("  [2/4] 生成配置清单...")
        manifest = self.manifest_generator.generate_manifest(agents, capability_registry)
        self.manifest_generator.save_manifest(manifest, f"{layer4_dir}/manifest.json")

        # 3. 链接知识库
        logger.info("  [3/4] 链接 RAG 知识库...")
        knowledge_links = self.rag_linker.link_knowledge(agents, domain)
        self.rag_linker.save_knowledge_links(knowledge_links, f"{layer4_dir}/knowledge_links.json")

        # 4. 生成监控配置
        logger.info("  [4/4] 生成监控配置...")
        monitoring_config = self.monitoring_generator.generate_monitoring_config(
            agents,
            capability_registry
        )
        self.monitoring_generator.save_monitoring_config(monitoring_config, f"{layer4_dir}/monitoring")

        result = {
            "prompts_count": len(prompts),
            "manifest": manifest,
            "knowledge_links": knowledge_links,
            "monitoring_config": monitoring_config
        }

        logger.info(f"\n  生成了 {len(prompts)} 个 Agent Prompt")
        logger.info(f"  配置清单已保存")
        logger.info(f"  知识库链接已配置")
        logger.info(f"  监控配置已生成")

        return result
