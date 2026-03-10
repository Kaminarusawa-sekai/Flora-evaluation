"""
监控配置生成器 - 生成可观测性配置
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from typing import Dict, Any, List
from shared.logger import get_logger
from shared.utils import save_json, save_yaml

logger = get_logger(__name__)


class MonitoringConfigGenerator:
    """监控配置生成器"""

    def generate_monitoring_config(
        self,
        agents: List[Dict[str, Any]],
        capability_registry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        生成监控配置

        Args:
            agents: Agent 列表
            capability_registry: 能力注册表

        Returns:
            监控配置
        """
        logger.info("Generating monitoring configuration")

        config = {
            "metrics": self._generate_metrics(agents),
            "alerts": self._generate_alerts(agents),
            "dashboards": self._generate_dashboards(agents),
            "logging": self._generate_logging_config()
        }

        logger.info("Monitoring configuration generated")
        return config

    def _generate_metrics(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成指标配置"""
        metrics = []

        # 全局指标
        metrics.extend([
            {
                "name": "agent_total_requests",
                "type": "counter",
                "description": "Agent 总请求数",
                "labels": ["agent_id", "agent_name"]
            },
            {
                "name": "agent_request_duration_seconds",
                "type": "histogram",
                "description": "Agent 请求处理时长",
                "labels": ["agent_id", "agent_name"],
                "buckets": [0.1, 0.5, 1.0, 2.0, 5.0, 10.0]
            },
            {
                "name": "agent_errors_total",
                "type": "counter",
                "description": "Agent 错误总数",
                "labels": ["agent_id", "agent_name", "error_type"]
            },
            {
                "name": "agent_active_tasks",
                "type": "gauge",
                "description": "Agent 当前活跃任务数",
                "labels": ["agent_id", "agent_name"]
            }
        ])

        # 为每个 Agent 生成特定指标
        for agent in agents:
            agent_id = agent['agent_id']
            agent_name = agent['agent_name']

            # API 调用指标
            metrics.append({
                "name": f"{agent_id}_api_calls_total",
                "type": "counter",
                "description": f"{agent_name} API 调用总数",
                "labels": ["api_name", "status"]
            })

            # 能力使用指标
            metrics.append({
                "name": f"{agent_id}_capability_usage",
                "type": "counter",
                "description": f"{agent_name} 能力使用次数",
                "labels": ["capability_name"]
            })

        return metrics

    def _generate_alerts(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成告警规则"""
        alerts = []

        # 全局告警
        alerts.extend([
            {
                "name": "HighErrorRate",
                "condition": "agent_errors_total / agent_total_requests > 0.1",
                "duration": "5m",
                "severity": "warning",
                "description": "Agent 错误率超过 10%",
                "actions": ["notify_admin", "log"]
            },
            {
                "name": "SlowResponse",
                "condition": "agent_request_duration_seconds > 10",
                "duration": "2m",
                "severity": "warning",
                "description": "Agent 响应时间超过 10 秒",
                "actions": ["notify_admin"]
            },
            {
                "name": "AgentDown",
                "condition": "up{job='agents'} == 0",
                "duration": "1m",
                "severity": "critical",
                "description": "Agent 服务不可用",
                "actions": ["notify_admin", "page_oncall"]
            }
        ])

        # 为关键 Agent 生成特定告警
        critical_agents = [a for a in agents if a['level'] in ['supervisor', 'manager']]

        for agent in critical_agents:
            agent_id = agent['agent_id']
            agent_name = agent['agent_name']

            alerts.append({
                "name": f"{agent_id}_HighLoad",
                "condition": f"agent_active_tasks{{agent_id='{agent_id}'}} > 10",
                "duration": "5m",
                "severity": "warning",
                "description": f"{agent_name} 负载过高",
                "actions": ["notify_admin"]
            })

        return alerts

    def _generate_dashboards(self, agents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """生成仪表板配置"""
        dashboards = []

        # 总览仪表板
        dashboards.append({
            "name": "Agent System Overview",
            "panels": [
                {
                    "title": "总请求数",
                    "type": "graph",
                    "metric": "sum(agent_total_requests)"
                },
                {
                    "title": "平均响应时间",
                    "type": "graph",
                    "metric": "avg(agent_request_duration_seconds)"
                },
                {
                    "title": "错误率",
                    "type": "graph",
                    "metric": "sum(agent_errors_total) / sum(agent_total_requests)"
                },
                {
                    "title": "活跃 Agent 数",
                    "type": "gauge",
                    "metric": "count(up{job='agents'} == 1)"
                }
            ]
        })

        # 按层级的仪表板
        levels = set(agent['level'] for agent in agents)
        for level in levels:
            dashboards.append({
                "name": f"{level.capitalize()} Agents Dashboard",
                "panels": [
                    {
                        "title": f"{level} 请求数",
                        "type": "graph",
                        "metric": f"sum(agent_total_requests{{level='{level}'}})"
                    },
                    {
                        "title": f"{level} 错误数",
                        "type": "graph",
                        "metric": f"sum(agent_errors_total{{level='{level}'}})"
                    }
                ]
            })

        return dashboards

    def _generate_logging_config(self) -> Dict[str, Any]:
        """生成日志配置"""
        return {
            "level": "INFO",
            "format": "json",
            "output": {
                "type": "file",
                "path": "./logs/agents.log",
                "rotation": {
                    "max_size": "100MB",
                    "max_age": "30d",
                    "max_backups": 10
                }
            },
            "fields": [
                "timestamp",
                "level",
                "agent_id",
                "agent_name",
                "message",
                "trace_id",
                "duration_ms"
            ],
            "sampling": {
                "enabled": True,
                "rate": 0.1  # 采样 10%
            }
        }

    def generate_prometheus_config(
        self,
        agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成 Prometheus 配置"""
        return {
            "global": {
                "scrape_interval": "15s",
                "evaluation_interval": "15s"
            },
            "scrape_configs": [
                {
                    "job_name": "agents",
                    "static_configs": [
                        {
                            "targets": ["localhost:9090"],
                            "labels": {
                                "environment": "production"
                            }
                        }
                    ]
                }
            ]
        }

    def generate_grafana_dashboard(
        self,
        agents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """生成 Grafana 仪表板 JSON"""
        return {
            "dashboard": {
                "title": "Agent System Monitoring",
                "panels": [
                    {
                        "id": 1,
                        "title": "Request Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(agent_total_requests[5m])"
                            }
                        ]
                    },
                    {
                        "id": 2,
                        "title": "Error Rate",
                        "type": "graph",
                        "targets": [
                            {
                                "expr": "rate(agent_errors_total[5m])"
                            }
                        ]
                    }
                ]
            }
        }

    def save_monitoring_config(self, config: Dict[str, Any], output_dir: str):
        """保存监控配置"""
        from pathlib import Path

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 保存主配置
        save_json(config, str(output_path / "monitoring.json"))

        # 保存 Prometheus 配置
        if 'prometheus' in config:
            save_yaml(config['prometheus'], str(output_path / "prometheus.yml"))

        # 保存 Grafana 仪表板
        if 'grafana' in config:
            save_json(config['grafana'], str(output_path / "grafana_dashboard.json"))

        logger.info(f"Monitoring configuration saved to {output_dir}")
