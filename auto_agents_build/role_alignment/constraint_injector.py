"""
约束注入器 - 为敏感 API 添加业务约束
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger
from shared.llm_client import LLMClient

logger = get_logger(__name__)


class ConstraintInjector:
    """约束注入器"""

    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def inject_constraints(
        self,
        roles: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        为角色的 API 注入业务约束

        Args:
            roles: 角色列表

        Returns:
            {
                "roles_with_constraints": [...],
                "contracts": [...]
            }
        """
        logger.info("Injecting constraints into roles")

        roles_with_constraints = []
        all_contracts = []

        for role in roles:
            role_name = role['role_name']
            assigned_apis = role.get('assigned_apis', [])

            # 识别敏感 API
            sensitive_apis = self._identify_sensitive_apis(assigned_apis)

            # 为敏感 API 生成约束
            constraints = self._generate_constraints(role, sensitive_apis)

            # 更新角色
            updated_role = role.copy()
            updated_role['constraints'] = constraints
            updated_role['sensitive_api_count'] = len(sensitive_apis)

            # 更新 API 的约束信息
            updated_apis = []
            for api in assigned_apis:
                api_copy = api.copy()
                api_id = api['api_id']

                # 查找该 API 的约束
                api_constraints = [c for c in constraints if c.get('api_id') == api_id]
                if api_constraints:
                    api_copy['constraints'] = api_constraints

                updated_apis.append(api_copy)

            updated_role['assigned_apis'] = updated_apis

            roles_with_constraints.append(updated_role)

            # 生成契约
            contracts = self._generate_contracts(role, constraints)
            all_contracts.extend(contracts)

            logger.info(f"  {role_name}: {len(constraints)} constraints, {len(contracts)} contracts")

        result = {
            "roles_with_constraints": roles_with_constraints,
            "contracts": all_contracts
        }

        logger.info(f"Constraint injection completed: {len(all_contracts)} contracts generated")
        return result

    def _identify_sensitive_apis(self, apis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """识别敏感 API"""
        sensitive = []

        sensitive_keywords = [
            'delete', 'remove', 'drop', 'truncate',  # 删除操作
            'update', 'modify', 'edit', 'change',     # 修改操作
            'approve', 'reject', 'audit',             # 审批操作
            'payment', 'transfer', 'refund',          # 财务操作
            'password', 'secret', 'token',            # 安全相关
            'admin', 'privilege', 'permission'        # 权限相关
        ]

        for api in apis:
            api_name = api.get('api_name', '').lower()
            api_path = api.get('path', '').lower()
            method = api.get('method', '').upper()

            # 检查是否包含敏感关键词
            is_sensitive = any(keyword in api_name or keyword in api_path
                             for keyword in sensitive_keywords)

            # DELETE/PUT 方法通常是敏感的
            if method in ['DELETE', 'PUT', 'PATCH']:
                is_sensitive = True

            if is_sensitive:
                sensitive.append(api)

        return sensitive

    def _generate_constraints(
        self,
        role: Dict[str, Any],
        sensitive_apis: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """为敏感 API 生成约束"""
        if not sensitive_apis:
            return []

        role_name = role['role_name']
        role_level = role.get('level', 'specialist')

        constraints = []

        for api in sensitive_apis:
            api_id = api['api_id']
            api_name = api['api_name']
            method = api.get('method', 'GET')

            # 基于规则的约束
            rule_constraints = self._rule_based_constraints(api, role_level)

            # LLM 生成的约束
            llm_constraints = self._llm_generate_constraints(api, role)

            # 合并约束
            all_constraints = rule_constraints + llm_constraints

            for constraint in all_constraints:
                constraints.append({
                    "api_id": api_id,
                    "api_name": api_name,
                    "constraint_type": constraint['type'],
                    "constraint_rule": constraint['rule'],
                    "description": constraint['description']
                })

        return constraints

    def _rule_based_constraints(self, api: Dict[str, Any], role_level: str) -> List[Dict[str, Any]]:
        """基于规则的约束"""
        constraints = []
        method = api.get('method', 'GET')
        api_name = api.get('api_name', '').lower()

        # 删除操作需要审批
        if method == 'DELETE' or 'delete' in api_name:
            if role_level == 'specialist':
                constraints.append({
                    "type": "approval_required",
                    "rule": "需要主管审批",
                    "description": "删除操作需要上级主管审批后才能执行"
                })

        # 财务操作需要金额限制
        if any(keyword in api_name for keyword in ['payment', 'transfer', 'refund']):
            constraints.append({
                "type": "amount_limit",
                "rule": "金额 > 10000 需审批",
                "description": "超过10000元的财务操作需要审批"
            })

        # 数据隔离
        if method in ['GET', 'POST', 'PUT', 'DELETE']:
            constraints.append({
                "type": "data_isolation",
                "rule": "只能操作本人/本部门数据",
                "description": "自动添加 owner_id 或 department_id 过滤条件"
            })

        return constraints

    def _llm_generate_constraints(self, api: Dict[str, Any], role: Dict[str, Any]) -> List[Dict[str, Any]]:
        """使用 LLM 生成约束"""
        api_name = api.get('api_name')
        api_desc = api.get('description', '')
        role_name = role['role_name']

        prompt = f"""为以下 API 生成业务约束规则。

API: {api_name}
描述: {api_desc}
角色: {role_name}

请考虑：
1. 是否需要审批流程
2. 是否需要金额/数量限制
3. 是否需要数据权限隔离
4. 是否需要操作日志审计

返回 JSON 格式：
{{
  "constraints": [
    {{
      "type": "约束类型",
      "rule": "约束规则",
      "description": "约束说明"
    }}
  ]
}}
"""

        try:
            response = self.llm_client.chat_with_json([
                {"role": "system", "content": "你是一个业务安全专家。"},
                {"role": "user", "content": prompt}
            ], temperature=0.2)

            return response.get('constraints', [])

        except Exception as e:
            logger.warning(f"LLM constraint generation failed for {api_name}: {e}")
            return []

    def _generate_contracts(
        self,
        role: Dict[str, Any],
        constraints: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成业务契约"""
        contracts = []

        for constraint in constraints:
            contract = {
                "contract_id": self._generate_contract_id(role['role_id'], constraint['api_id']),
                "role_id": role['role_id'],
                "role_name": role['role_name'],
                "api_id": constraint['api_id'],
                "api_name": constraint['api_name'],
                "constraint_type": constraint['constraint_type'],
                "constraint_rule": constraint['constraint_rule'],
                "enforcement": "pre_execution",  # 执行前检查
                "violation_action": "reject"      # 违反时拒绝
            }
            contracts.append(contract)

        return contracts

    def _generate_contract_id(self, role_id: str, api_id: str) -> str:
        """生成契约 ID"""
        import hashlib
        combined = f"{role_id}_{api_id}"
        return f"contract_{hashlib.md5(combined.encode()).hexdigest()[:8]}"
