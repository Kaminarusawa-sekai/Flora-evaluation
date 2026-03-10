"""
模板加载器 - 根据领域探测结果加载角色模板
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List, Optional
from shared.logger import get_logger
from shared.llm_client import LLMClient
from .functional_meta_library import FunctionalMetaLibrary

logger = get_logger(__name__)


class TemplateLoader:
    """模板加载器"""

    def __init__(self, meta_library: FunctionalMetaLibrary, llm_client: LLMClient):
        self.meta_library = meta_library
        self.llm_client = llm_client

    def load_templates(
        self,
        primary_domain: str,
        secondary_domains: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        加载角色模板

        Args:
            primary_domain: 主导领域
            secondary_domains: 次要领域列表

        Returns:
            角色模板列表
        """
        logger.info(f"Loading templates for domain: {primary_domain}")

        roles = []

        # 加载主导领域的模板
        primary_roles = self._load_domain_template(primary_domain)
        if primary_roles:
            roles.extend(primary_roles)
            logger.info(f"Loaded {len(primary_roles)} roles from {primary_domain}")
        else:
            # 无模板时使用 LLM 生成
            logger.warning(f"No template found for {primary_domain}, generating with LLM")
            generated_roles = self._generate_template_with_llm(primary_domain)
            roles.extend(generated_roles)

        # 加载次要领域的模板
        if secondary_domains:
            for domain in secondary_domains:
                domain_roles = self._load_domain_template(domain)
                if domain_roles:
                    roles.extend(domain_roles)
                    logger.info(f"Loaded {len(domain_roles)} roles from {domain}")

        # 去重（基于角色名称）
        unique_roles = self._deduplicate_roles(roles)

        logger.info(f"Total loaded roles: {len(unique_roles)}")
        return unique_roles

    def _load_domain_template(self, domain_name: str) -> List[Dict[str, Any]]:
        """加载领域模板"""
        domain = self.meta_library.get_domain(domain_name)
        if domain:
            return domain.get('roles', [])
        return []

    def _generate_template_with_llm(self, domain_name: str) -> List[Dict[str, Any]]:
        """使用 LLM 生成新的领域模板"""
        prompt = f"""为"{domain_name}"领域生成标准的职能角色模板。

请生成3-5个典型角色，包括基层专员、中层主管等。

返回 JSON 格式：
{{
  "roles": [
    {{
      "role_name": "角色名称",
      "level": "specialist/supervisor/manager",
      "responsibilities": ["职责1", "职责2"],
      "required_capabilities": ["必需能力1", "必需能力2"],
      "optional_capabilities": ["可选能力1"]
    }}
  ]
}}
"""

        try:
            response = self.llm_client.chat_with_json([
                {"role": "system", "content": "你是一个组织架构设计专家。"},
                {"role": "user", "content": prompt}
            ])

            roles = response.get('roles', [])

            # 保存到元库
            domain_data = {
                "domain_name": domain_name,
                "keywords": [],
                "roles": roles
            }
            self.meta_library.add_domain(domain_name, domain_data)
            self.meta_library.save()

            logger.info(f"Generated {len(roles)} roles for {domain_name}")
            return roles

        except Exception as e:
            logger.error(f"Failed to generate template with LLM: {e}")
            return []

    def _deduplicate_roles(self, roles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """去重角色（基于角色名称）"""
        seen = set()
        unique = []

        for role in roles:
            role_name = role.get('role_name')
            if role_name and role_name not in seen:
                seen.add(role_name)
                unique.append(role)

        return unique

    def merge_templates(
        self,
        primary_roles: List[Dict[str, Any]],
        secondary_roles: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        合并多个领域的模板

        Args:
            primary_roles: 主导领域角色
            secondary_roles: 次要领域角色

        Returns:
            合并后的角色列表
        """
        # 主导领域角色优先
        merged = primary_roles.copy()

        # 添加次要领域的角色（如果不重复）
        primary_names = {role['role_name'] for role in primary_roles}

        for role in secondary_roles:
            if role['role_name'] not in primary_names:
                merged.append(role)

        return merged
