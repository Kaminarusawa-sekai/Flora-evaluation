"""Generate test scenarios using LLM."""

from typing import List, Dict, Any, Optional, Literal
import json
from models import TestScenario, ParameterConstraint, InjectionPoint


class ScenarioGenerator:
    """Generate business test scenarios from API paths using LLM."""

    def __init__(self, llm_config: Dict[str, Any] = None):
        self.llm_config = llm_config or {}
        self.injection_modes = {
            "missing_link": "故意跳过路径中的一步",
            "state_conflict": "在不兼容的状态下调用接口",
            "permission_gap": "使用无权限的账号调用接口",
            "invalid_data": "使用非法参数（空值、超长、特殊字符）"
        }

    def generate(self, api_path: List[str],
                 api_details: Optional[Dict[str, Dict[str, Any]]] = None,
                 scenario_type: Literal["normal", "exception", "boundary"] = "normal",
                 parameter_flow: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate a test scenario with dynamic parameter references."""
        context = self._build_enhanced_context(api_path, api_details, parameter_flow)
        prompt = self._build_prompt(context, scenario_type)

        # TODO: Replace with actual LLM call
        scenario = self._generate_from_template(context, scenario_type, parameter_flow)

        return scenario

    def _build_enhanced_context(self, api_path: List[str],
                                api_details: Optional[Dict[str, Dict[str, Any]]],
                                parameter_flow: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Build enhanced context with parameter flow."""
        context = {
            "api_path": api_path,
            "api_summaries": [],
            "parameter_dependencies": {}
        }

        for i, op_id in enumerate(api_path):
            summary = {"step": i, "operation_id": op_id}
            if api_details and op_id in api_details:
                detail = api_details[op_id]
                summary.update({
                    "method": detail.get("method"),
                    "path": detail.get("path"),
                    "summary": detail.get("summary", ""),
                    "key_inputs": self._extract_key_fields(detail.get("parameters", [])),
                    "key_outputs": self._extract_key_fields(detail.get("responses", {}))
                })
            context["api_summaries"].append(summary)

        if parameter_flow:
            context["parameter_dependencies"] = parameter_flow

        return context

    def _extract_key_fields(self, schema: Any) -> List[str]:
        """Extract key field names from schema (minimal extraction)."""
        if isinstance(schema, dict):
            return list(schema.keys())[:3]  # Only top 3 fields
        elif isinstance(schema, list):
            return [p.get("name", "") for p in schema[:3] if isinstance(p, dict)]
        return []

    def _build_prompt(self, context: Dict[str, Any], scenario_type: str) -> str:
        """Build LLM prompt based on scenario type."""
        base_prompt = f"基于以下API路径生成测试场景：\n{json.dumps(context['api_summaries'], ensure_ascii=False, indent=2)}\n\n"

        if scenario_type == "normal":
            base_prompt += "要求：\n1. 生成流程顺畅的正常业务场景\n2. 对于依赖上游输出的参数（如ID、Token），使用 {{step_name.response.field_path}} 格式\n3. 对于独立参数（如备注、数量），生成合理的假数据或使用 {{fake_email}}, {{fake_name}} 等占位符"
        elif scenario_type == "exception":
            base_prompt += f"要求：\n1. 明确指出在第几步注入错误\n2. 可选的注入模式：{', '.join(self.injection_modes.keys())}\n3. 描述预期的错误码或错误信息\n4. 确保错误注入的逻辑合理性"
        elif scenario_type == "boundary":
            base_prompt += "要求：\n1. 针对参数使用极值（最大长度、最小值、空值、特殊字符）\n2. 测试系统的边界处理能力"

        return base_prompt

    def _generate_from_template(self, context: Dict[str, Any], scenario_type: str,
                                parameter_flow: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate scenario with dynamic references."""
        summaries = context["api_summaries"]

        scenario = {
            'title': self._generate_title(summaries, scenario_type),
            'description': self._generate_description(summaries, scenario_type),
            'scenario_type': scenario_type,
            'steps': [s["operation_id"] for s in summaries],
            'parameter_bindings': self._generate_parameter_bindings(summaries, parameter_flow),
            'expected_outcome': self._generate_expected_outcome(summaries, scenario_type),
            'dependency_map': self._build_dependency_map(summaries, parameter_flow)
        }

        if scenario_type == "exception":
            scenario['injection_point'] = self._generate_injection_point(summaries)

        return scenario

    def _generate_parameter_bindings(self, summaries: List[Dict],
                                     parameter_flow: Optional[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Generate parameter bindings with dynamic references."""
        bindings = {}

        for i, summary in enumerate(summaries):
            op_id = summary["operation_id"]
            step_bindings = {}

            # Check if this step has upstream dependencies
            if parameter_flow and op_id in parameter_flow:
                for param, source in parameter_flow[op_id].items():
                    if isinstance(source, str) and "." in source:  # Dynamic reference
                        step_bindings[param] = {
                            "type": "dynamic_ref",
                            "value": f"{{{source}}}"
                        }
                    else:
                        step_bindings[param] = {
                            "type": "static",
                            "value": source
                        }
            else:
                # Generate fake data for independent parameters
                for field in summary.get("key_inputs", []):
                    if "id" in field.lower() and i > 0:
                        step_bindings[field] = {
                            "type": "dynamic_ref",
                            "value": f"{{{summaries[i-1]['operation_id']}.response.id}}"
                        }
                    elif "email" in field.lower():
                        step_bindings[field] = {"type": "fake_data", "value": "{{fake_email}}"}
                    elif "name" in field.lower():
                        step_bindings[field] = {"type": "fake_data", "value": "{{fake_name}}"}

            if step_bindings:
                bindings[op_id] = step_bindings

        return bindings

    def _build_dependency_map(self, summaries: List[Dict],
                              parameter_flow: Optional[Dict[str, Any]]) -> Dict[str, str]:
        """Build step dependency map."""
        dep_map = {}
        for i, summary in enumerate(summaries):
            if i > 0:
                dep_map[summary["operation_id"]] = summaries[i-1]["operation_id"]
        return dep_map

    def _generate_injection_point(self, summaries: List[Dict]) -> Dict[str, Any]:
        """Generate error injection point for exception scenarios."""
        inject_step = len(summaries) // 2  # Inject at middle step
        return {
            "step_index": inject_step,
            "injection_type": "invalid_data",
            "description": f"在步骤 {inject_step} 注入非法参数",
            "expected_error": "400 Bad Request"
        }

    def _generate_title(self, summaries: List[Dict], scenario_type: str) -> str:
        """Generate scenario title."""
        if not summaries:
            return "API Test Scenario"

        verbs = []
        for s in summaries:
            method = s.get("method", "")
            if method == "POST" or "create" in s["operation_id"].lower():
                verbs.append("创建")
            elif method == "GET" or "list" in s["operation_id"].lower():
                verbs.append("查询")
            elif method == "PUT" or "update" in s["operation_id"].lower():
                verbs.append("更新")
            elif method == "DELETE":
                verbs.append("删除")

        prefix = "异常场景" if scenario_type == "exception" else "正常场景"
        return f"{prefix}: {' -> '.join(verbs[:3])}" if verbs else f"{prefix}: API工作流测试"

    def _generate_description(self, summaries: List[Dict], scenario_type: str) -> str:
        """Generate scenario description."""
        ops = [s.get("summary", s["operation_id"]) for s in summaries]
        return f"测试场景覆盖 {len(summaries)} 个API操作: {' -> '.join(ops)}"

    def _generate_expected_outcome(self, summaries: List[Dict], scenario_type: str) -> str:
        """Generate expected outcome."""
        if scenario_type == "exception":
            return "应返回预期的错误码，系统正确处理异常情况"
        return "所有API调用成功，工作流正常完成"
