"""
API 规范化模块适配器
"""

from core.module_adapter import ModuleAdapter
from common.schemas import Stage1Output, Capability
from typing import Dict


class NormalizationAdapter(ModuleAdapter):
    """API 规范化模块适配器"""

    def __init__(self):
        from api_normalization import NormalizationService
        self.service = None
        self.refiner = None

    def process(self, input_data: Dict, config: Dict) -> Stage1Output:
        from api_normalization import NormalizationService
        from api_normalization.llm_cluster_refiner import LLMClusterRefiner

        # 提取 LLM refiner 配置
        use_llm_refiner = config.pop('use_llm_refiner', False)
        llm_config = config.pop('llm_refiner_config', {})

        if not self.service:
            self.service = NormalizationService(**config)

        # 适配输入格式
        # input_data 可能是：
        # 1. 已加载的 Swagger 字典对象（从 pipeline_orchestrator 传来）
        # 2. 包含 'path' 键的字典
        # 3. 字符串路径
        if isinstance(input_data, dict) and 'path' in input_data:
            swagger_source = input_data['path']
        else:
            swagger_source = input_data

        # 执行初始处理
        parsed = self.service.parser.parse(swagger_source)
        clustered_apis = self.service.clusterer.cluster(parsed['apis'])

        # 如果启用 LLM refiner，则进行重新分类和命名
        if use_llm_refiner:
            if not self.refiner:
                self.refiner = LLMClusterRefiner(**llm_config)
            
            print("\n[LLM Refiner] 开始使用 LLM 重新分类和命名 entity...")
            clustered_apis = self.refiner.refine(clustered_apis)
            
            # 重要：更新所有 API 的 entity_anchor，确保使用 LLM 生成的名称
            self._update_entity_anchors(clustered_apis)
            print("[LLM Refiner] 完成\n")

        # 提取 capabilities
        capabilities_result = self.service.extractor.extract(clustered_apis)

        # 构建结果
        result = {
            'capabilities': capabilities_result['capabilities'],
            'statistics': {
                'total_apis': capabilities_result['total_apis'],
                'total_capabilities': capabilities_result['total_capabilities'],
                'semantic_capabilities': capabilities_result.get('semantic_capabilities', 0),
                'atomic_capabilities': capabilities_result.get('atomic_capabilities', 0)
            },
            'source': {
                'title': parsed['title'],
                'version': parsed['version'],
                'source': swagger_source
            }
        }

        # 适配输出格式
        return Stage1Output(
            capabilities=[Capability(**cap) for cap in result['capabilities']],
            statistics=result.get('statistics', {}),
            metadata={
                'stage': 'normalization',
                'version': '1.0.0',
                'llm_refined': use_llm_refiner
            }
        )

    def validate_input(self, input_data: Dict) -> bool:
        # 验证输入是否为有效的 Swagger 文件路径
        return isinstance(input_data, (str, dict))

    def _update_entity_anchors(self, clustered_apis: list) -> None:
        """
        更新所有 API 的 entity_anchor，确保使用 LLM 优化后的名称。
        
        策略：
        1. 对于 LLM 创建的新组（有 group_name），使用 group_name 作为 entity_anchor
        2. 对于合并到现有集群的 API，使用该集群中最常见的 entity_anchor
        3. 对于原子 API，保持原有的 entity_anchor（除非是 'unknown'）
        4. 对于 'unknown' 的 entity，尝试从路径或 LLM reason 中提取更好的名称
        """
        from collections import Counter
        import re
        
        # 按集群分组
        clusters = {}
        for api in clustered_apis:
            cluster_id = api.get('cluster', -1)
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(api)
        
        updated_count = 0
        
        # 为每个集群确定统一的 entity_anchor
        for cluster_id, apis in clusters.items():
            if len(apis) == 1:
                # 单个 API
                api = apis[0]
                current_anchor = api.get('entity_anchor', 'unknown')
                
                # 如果是 unknown，尝试从 LLM reason 或 group_name 中提取
                if current_anchor == 'unknown':
                    if 'group_name' in api:
                        api['entity_anchor'] = api['group_name'].replace('_', '-')
                        updated_count += 1
                    elif 'llm_reason' in api:
                        # 尝试从 reason 中提取 entity 名称
                        reason = api['llm_reason'].lower()
                        # 简单的关键词提取
                        if 'statistics' in reason or 'reporting' in reason:
                            api['entity_anchor'] = 'statistics'
                            updated_count += 1
                        elif 'file' in reason or 'upload' in reason or 'download' in reason:
                            api['entity_anchor'] = 'file-operations'
                            updated_count += 1
                        elif 'status' in reason:
                            api['entity_anchor'] = 'status-management'
                            updated_count += 1
                continue
            
            # 多个 API 的集群
            # 优先级：group_name > 最常见的非 unknown entity_anchor > 从路径提取
            
            # 1. 检查是否有 LLM 生成的 group_name
            group_names = [api.get('group_name') for api in apis if 'group_name' in api]
            if group_names:
                # 使用最常见的 group_name
                group_name_counts = Counter(group_names)
                unified_anchor = group_name_counts.most_common(1)[0][0].replace('_', '-')
            else:
                # 2. 使用最常见的非 unknown entity_anchor
                entity_anchors = [api.get('entity_anchor', 'unknown') for api in apis 
                                if api.get('entity_anchor', 'unknown') != 'unknown']
                
                if entity_anchors:
                    anchor_counts = Counter(entity_anchors)
                    unified_anchor = anchor_counts.most_common(1)[0][0]
                else:
                    # 3. 所有都是 unknown，尝试从路径中提取
                    # 收集所有路径段
                    all_segments = []
                    for api in apis:
                        path = api.get('path', '')
                        segments = [s for s in path.split('/') if s and not s.startswith('{')]
                        all_segments.extend(segments)
                    
                    if all_segments:
                        segment_counts = Counter(all_segments)
                        # 排除常见的噪音词
                        noise_words = {'api', 'v1', 'v2', 'v3', 'admin', 'erp', 'public'}
                        for segment, count in segment_counts.most_common():
                            if segment.lower() not in noise_words:
                                unified_anchor = segment.lower()
                                break
                        else:
                            unified_anchor = f'cluster-{cluster_id}'
                    else:
                        unified_anchor = f'cluster-{cluster_id}'
            
            # 更新集群中所有 API 的 entity_anchor
            for api in apis:
                old_anchor = api.get('entity_anchor', 'unknown')
                if old_anchor != unified_anchor:
                    api['entity_anchor'] = unified_anchor
                    updated_count += 1
                
        print(f"  已更新 {updated_count} 个 API 的 entity_anchor")
        
        # 统计最终的 entity 分布
        entity_counts = Counter(api.get('entity_anchor', 'unknown') for api in clustered_apis)
        print(f"  最终 entity 分布: {len(entity_counts)} 个不同的 entity")
        unknown_count = entity_counts.get('unknown', 0)
        if unknown_count > 0:
            print(f"  ⚠️  仍有 {unknown_count} 个 API 的 entity 为 'unknown'")
        else:
            print(f"  ✓ 所有 API 都已正确命名 entity")

    def get_metadata(self) -> Dict:
        return {
            'name': 'API Normalization',
            'version': '1.0.0',
            'description': 'Normalize Swagger/OpenAPI documents',
            'input_format': 'swagger_json',
            'output_format': 'capabilities_json'
        }
