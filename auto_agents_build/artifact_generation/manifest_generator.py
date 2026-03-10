"""
配置清单生成器 - 生成数字孪生配置
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger
from shared.utils import save_json

logger = get_logger(__name__)


class ManifestGenerator:
    """配置清单生成器"""

    def generate_manifest(
        self,
        agents: List[Dict[str, Any]],
        capability_registry: Dict[str, Any],
        environment: str = "production"
    ) -> Dict[str, Any]:
        """
        生成 manifest.json

        Args:
            agents: Agent 列表
            capability_registry: 能力注册表
            environment: 环境 (dev/staging/production)

        Returns:
            manifest 配置
        """
        logger.info(f"Generating manifest for {environment} environment")

        manifest = {
            "version": "1.0",
            "environment": environment,
            "agents": self._format_agent_configs(agents, capability_registry),
            "api_endpoints": self._extract_api_endpoints(capability_registry, environment),
            "authentication": self._generate_auth_config(environment),
            "rag_config": self._generate_rag_config(environment),
            "runtime_config": self._generate_runtime_config(environment)
        }

        logger.info("Manifest generated successfully")
        return manifest

    def _format_agent_configs(
        self,
        agents: List[Dict[str, Any]],
        capability_registry: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """格式化 Agent 配置"""
        configs = []

        for agent in agents:
            config = {
                "agent_id": agent['agent_id'],
                "agent_name": agent['agent_name'],
                "agent_type": agent['level'],
                "enabled": True,
                "capabilities": self._get_capability_names(agent, capability_registry),
                "subordinates": agent.get('subordinates', []),
                "memory": {
                    "type": agent.get('local_memory', {}).get('type', 'short_term'),
                    "capacity": agent.get('local_memory', {}).get('capacity', '1000_messages')
                },
                "prompt_file": f"prompts/{agent['agent_id']}.txt",
                "max_iterations": 10,
                "timeout": 300
            }

            configs.append(config)

        return configs

    def _get_capability_names(
        self,
        agent: Dict[str, Any],
        capability_registry: Dict[str, Any]
    ) -> List[str]:
        """获取能力名称列表"""
        interface = agent.get('capability_interface', {})
        all_cap_refs = (
            interface.get('direct_capabilities', []) +
            interface.get('composed_capabilities', []) +
            interface.get('delegated_capabilities', [])
        )

        all_units = (
            capability_registry.get('atomic_capabilities', []) +
            capability_registry.get('composed_capabilities', []) +
            capability_registry.get('strategic_capabilities', [])
        )
        unit_map = {unit['unit_id']: unit['name'] for unit in all_units}

        return [unit_map.get(cap['unit_id'], cap['unit_id']) for cap in all_cap_refs]

    def _extract_api_endpoints(
        self,
        capability_registry: Dict[str, Any],
        environment: str
    ) -> Dict[str, str]:
        """提取 API 端点配置"""
        # 从原子能力中提取 API
        atomic_caps = capability_registry.get('atomic_capabilities', [])

        endpoints = {}
        base_url = self._get_base_url(environment)

        for cap in atomic_caps:
            for api in cap.get('underlying_apis', []):
                # 解析 API 格式: "POST /api/order/create"
                parts = api.split(' ', 1)
                if len(parts) == 2:
                    method, path = parts
                    endpoint_key = f"{method.lower()}_{path.replace('/', '_').strip('_')}"
                    endpoints[endpoint_key] = f"{base_url}{path}"

        return endpoints

    def _get_base_url(self, environment: str) -> str:
        """获取基础 URL"""
        urls = {
            "dev": "http://localhost:8000",
            "staging": "https://staging-api.example.com",
            "production": "https://api.example.com"
        }
        return urls.get(environment, urls['production'])

    def _generate_auth_config(self, environment: str) -> Dict[str, Any]:
        """生成认证配置"""
        return {
            "type": "bearer_token",
            "token_env_var": "API_TOKEN",
            "refresh_enabled": True,
            "refresh_interval": 3600
        }

    def _generate_rag_config(self, environment: str) -> Dict[str, Any]:
        """生成 RAG 配置"""
        return {
            "enabled": True,
            "vector_store": {
                "type": "faiss",
                "index_path": "./data/rag_index"
            },
            "embedding_model": "text-embedding-ada-002",
            "retrieval": {
                "top_k": 5,
                "similarity_threshold": 0.7
            }
        }

    def _generate_runtime_config(self, environment: str) -> Dict[str, Any]:
        """生成运行时配置"""
        return {
            "llm": {
                "provider": "openai",
                "model": "gpt-4" if environment == "production" else "gpt-3.5-turbo",
                "temperature": 0.3,
                "max_tokens": 2000
            },
            "logging": {
                "level": "INFO" if environment == "production" else "DEBUG",
                "format": "json",
                "output": "stdout"
            },
            "monitoring": {
                "enabled": True,
                "metrics_port": 9090,
                "health_check_interval": 60
            }
        }

    def generate_multi_env_manifests(
        self,
        agents: List[Dict[str, Any]],
        capability_registry: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        """生成多环境配置"""
        environments = ['dev', 'staging', 'production']
        manifests = {}

        for env in environments:
            manifests[env] = self.generate_manifest(agents, capability_registry, env)

        return manifests

    def save_manifest(self, manifest: Dict[str, Any], output_path: str):
        """保存 manifest 到文件"""
        save_json(manifest, output_path)
        logger.info(f"Manifest saved to {output_path}")
