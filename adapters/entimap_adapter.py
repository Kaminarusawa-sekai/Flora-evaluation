"""
数据库映射模块适配器
"""

from core.module_adapter import ModuleAdapter
from schemas.schemas import Stage3AOutput, TableMapping, FieldMapping, GoldenSQL
from typing import Dict


class EntiMapAdapter(ModuleAdapter):
    """数据库映射模块适配器"""

    def __init__(self):
        self.engine = None

    def process(self, input_data: Dict, config: Dict) -> Stage3AOutput:
        from ddl_entimap import EntiMapEngine

        if not self.engine:
            self.engine = EntiMapEngine(
                db_url=config['db_url'],
                api_key=config.get('api_key'),
                base_url=config.get('base_url'),
                model=config.get('model', 'qwen-plus')
            )

        # 提取 capabilities
        capabilities = input_data.get('capabilities', [])

        # 转换为实体列表
        entities = self._convert_capabilities_to_entities(capabilities)

        # 执行映射
        all_mappings = []
        all_golden_sqls = []
        vanna_data = {}

        for entity in entities:
            if entity['name']!=entities[0]['name']:
                continue
            # 对齐实体
            results = self.engine.align_entity(entity, top_k=10)

            # 收集映射 - results 是字典 {table_name: alignment_result}
            for table_name, result in results.items():
                # 提取 field_mapping (注意是单数形式)
                field_mapping_dict = result.get('field_mapping', {})
                field_mappings = []
                
                # 将字典转换为 FieldMapping 列表
                for api_field, db_field_info in field_mapping_dict.items():
                    if isinstance(db_field_info, dict):
                        # 从 columns_role 获取角色信息
                        columns_role = result.get('columns_role', {})
                        db_column = db_field_info.get('db_field', '')
                        role = 'business'  # 默认值
                        
                        # 查找该列的角色
                        for role_type, columns in columns_role.items():
                            if db_column in columns:
                                role = role_type
                                break
                        
                        field_mappings.append(FieldMapping(
                            db_column=db_column,
                            api_field=api_field,
                            role=role,
                            confidence=db_field_info.get('confidence', 0.8)
                        ))
                
                mapping = TableMapping(
                    table_name=table_name,
                    entity_name=entity['name'],
                    relation_type=result.get('relation_type', 'core'),
                    relation_score=result.get('relation_score', 0.0),
                    field_mappings=field_mappings
                )
                all_mappings.append(mapping)

            # 生成 Golden SQL
            golden_sqls = self._generate_golden_sqls(entity, results)
            all_golden_sqls.extend(golden_sqls)

        return Stage3AOutput(
            entity_mappings=all_mappings,
            golden_sqls=all_golden_sqls,
            vanna_training_data=vanna_data,
            metadata={
                'stage': 'database_mapping',
                'version': '1.0.0',
                'total_entities': len(entities),
                'total_mappings': len(all_mappings)
            }
        )

    def _convert_capabilities_to_entities(self, capabilities: list) -> list:
        """将 capabilities 转换为实体列表"""
        entities = []

        for cap in capabilities:
            # 提取 API 字段
            api_fields = []
            for api in cap.get('apis', []):
                # 从 unified_schema 提取字段
                schema = cap.get('unified_schema', {})
                properties = schema.get('properties', {})

                for field_name, field_info in properties.items():
                    api_fields.append({
                        'name': field_name,
                        'type': field_info.get('type', 'string'),
                        'description': field_info.get('description', '')
                    })

            entities.append({
                'name': cap.get('resource', cap.get('name')),
                'description': cap.get('description', ''),
                'api_fields': api_fields,
                'api_paths': [api.get('path') for api in cap.get('apis', [])]
            })

        return entities

    def _generate_golden_sqls(self, entity: Dict, mappings: Dict) -> list:
        """生成 Golden SQL"""
        golden_sqls = []

        entity_name = entity['name']
        
        # mappings 是字典 {table_name: alignment_result}
        if not mappings:
            return golden_sqls
        
        # 获取第一个表名（得分最高的）
        first_table = next(iter(mappings.keys()))

        # 基础查询
        golden_sqls.append(GoldenSQL(
            question=f"查询所有{entity_name}",
            sql=f"SELECT * FROM {first_table} WHERE deleted = 0",
            entity=entity_name
        ))

        return golden_sqls

    def validate_input(self, input_data: Dict) -> bool:
        return 'capabilities' in input_data

    def get_metadata(self) -> Dict:
        return {
            'name': 'Database Mapping',
            'version': '1.0.0',
            'description': 'Map API entities to database tables',
            'input_format': 'capabilities_json',
            'output_format': 'entity_mapping_json'
        }
