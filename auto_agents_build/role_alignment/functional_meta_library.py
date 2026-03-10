"""
全领域职能元库 - 预置多领域标准角色库
"""
import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent))

from shared.logger import get_logger
from shared.utils import load_json, save_json, ensure_dir

logger = get_logger(__name__)


class FunctionalMetaLibrary:
    """全领域职能元库"""

    def __init__(self, library_path: Optional[str] = None):
        self.library_path = library_path or "./templates/domains"
        ensure_dir(self.library_path)
        self.domains = {}
        self._load_library()

    def _load_library(self):
        """加载职能元库"""
        library_file = Path(self.library_path) / "meta_library.json"

        if library_file.exists():
            self.domains = load_json(str(library_file))
            logger.info(f"Loaded {len(self.domains)} domains from library")
        else:
            # 初始化默认领域
            self.domains = self._default_domains()
            self.save()
            logger.info("Initialized default domain library")

    def _default_domains(self) -> Dict[str, Any]:
        """默认领域模板"""
        return {
            "CRM": {
                "domain_name": "客户关系管理",
                "keywords": ["客户", "订单", "销售", "线索", "商机", "合同"],
                "roles": [
                    {
                        "role_name": "销售专员",
                        "level": "specialist",
                        "responsibilities": ["客户跟进", "订单创建", "报价管理"],
                        "required_capabilities": ["客户查询", "订单创建", "报价生成"],
                        "optional_capabilities": ["合同审核"]
                    },
                    {
                        "role_name": "销售主管",
                        "level": "supervisor",
                        "responsibilities": ["团队管理", "订单审批", "业绩分析"],
                        "required_capabilities": ["订单审批", "业绩统计", "团队管理"],
                        "optional_capabilities": ["客户分配"]
                    },
                    {
                        "role_name": "客户经理",
                        "level": "specialist",
                        "responsibilities": ["客户维护", "需求分析", "关系管理"],
                        "required_capabilities": ["客户信息管理", "沟通记录", "需求跟踪"],
                        "optional_capabilities": ["客户分级"]
                    }
                ]
            },
            "ERP": {
                "domain_name": "企业资源计划",
                "keywords": ["库存", "采购", "生产", "物料", "仓库", "供应链"],
                "roles": [
                    {
                        "role_name": "仓库专员",
                        "level": "specialist",
                        "responsibilities": ["库存管理", "出入库操作", "盘点"],
                        "required_capabilities": ["库存查询", "出入库记录", "库存调整"],
                        "optional_capabilities": ["库存预警"]
                    },
                    {
                        "role_name": "采购专员",
                        "level": "specialist",
                        "responsibilities": ["采购申请", "供应商管理", "订单跟踪"],
                        "required_capabilities": ["采购单创建", "供应商查询", "价格比较"],
                        "optional_capabilities": ["供应商评估"]
                    },
                    {
                        "role_name": "供应链主管",
                        "level": "supervisor",
                        "responsibilities": ["供应链协调", "采购审批", "库存优化"],
                        "required_capabilities": ["采购审批", "库存分析", "供应链监控"],
                        "optional_capabilities": ["供应商谈判"]
                    }
                ]
            },
            "Finance": {
                "domain_name": "财务管理",
                "keywords": ["财务", "会计", "发票", "付款", "收款", "报销", "账单"],
                "roles": [
                    {
                        "role_name": "会计专员",
                        "level": "specialist",
                        "responsibilities": ["凭证录入", "账目核对", "报表生成"],
                        "required_capabilities": ["凭证管理", "账目查询", "报表生成"],
                        "optional_capabilities": ["税务计算"]
                    },
                    {
                        "role_name": "出纳",
                        "level": "specialist",
                        "responsibilities": ["收付款管理", "现金管理", "银行对账"],
                        "required_capabilities": ["收款记录", "付款记录", "银行对账"],
                        "optional_capabilities": ["资金预测"]
                    },
                    {
                        "role_name": "财务主管",
                        "level": "supervisor",
                        "responsibilities": ["财务审批", "预算管理", "财务分析"],
                        "required_capabilities": ["付款审批", "预算监控", "财务报表"],
                        "optional_capabilities": ["成本分析"]
                    }
                ]
            },
            "HR": {
                "domain_name": "人力资源",
                "keywords": ["员工", "招聘", "考勤", "薪资", "绩效", "培训"],
                "roles": [
                    {
                        "role_name": "HR专员",
                        "level": "specialist",
                        "responsibilities": ["员工信息管理", "考勤管理", "招聘协助"],
                        "required_capabilities": ["员工信息录入", "考勤记录", "简历筛选"],
                        "optional_capabilities": ["入职办理"]
                    },
                    {
                        "role_name": "薪酬专员",
                        "level": "specialist",
                        "responsibilities": ["薪资计算", "社保管理", "个税申报"],
                        "required_capabilities": ["薪资计算", "社保缴纳", "个税申报"],
                        "optional_capabilities": ["薪资分析"]
                    },
                    {
                        "role_name": "HR主管",
                        "level": "supervisor",
                        "responsibilities": ["人力规划", "绩效管理", "团队建设"],
                        "required_capabilities": ["绩效评估", "人员配置", "培训计划"],
                        "optional_capabilities": ["人才发展"]
                    }
                ]
            },
            "MES": {
                "domain_name": "制造执行系统",
                "keywords": ["生产", "工单", "设备", "质检", "工艺", "车间"],
                "roles": [
                    {
                        "role_name": "生产专员",
                        "level": "specialist",
                        "responsibilities": ["工单执行", "生产记录", "进度跟踪"],
                        "required_capabilities": ["工单查询", "生产报工", "进度更新"],
                        "optional_capabilities": ["异常上报"]
                    },
                    {
                        "role_name": "质检员",
                        "level": "specialist",
                        "responsibilities": ["质量检验", "不良品处理", "质量记录"],
                        "required_capabilities": ["质检记录", "不良品登记", "质量报告"],
                        "optional_capabilities": ["质量分析"]
                    },
                    {
                        "role_name": "生产主管",
                        "level": "supervisor",
                        "responsibilities": ["生产调度", "资源协调", "效率优化"],
                        "required_capabilities": ["生产排程", "资源分配", "效率监控"],
                        "optional_capabilities": ["工艺优化"]
                    }
                ]
            }
        }

    def get_domain(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """获取领域模板"""
        return self.domains.get(domain_name)

    def get_all_domains(self) -> List[str]:
        """获取所有领域名称"""
        return list(self.domains.keys())

    def add_domain(self, domain_name: str, domain_data: Dict[str, Any]):
        """添加新领域"""
        self.domains[domain_name] = domain_data
        logger.info(f"Added domain: {domain_name}")

    def update_domain(self, domain_name: str, domain_data: Dict[str, Any]):
        """更新领域"""
        if domain_name in self.domains:
            self.domains[domain_name] = domain_data
            logger.info(f"Updated domain: {domain_name}")
        else:
            logger.warning(f"Domain not found: {domain_name}")

    def delete_domain(self, domain_name: str):
        """删除领域"""
        if domain_name in self.domains:
            del self.domains[domain_name]
            logger.info(f"Deleted domain: {domain_name}")

    def get_roles_by_domain(self, domain_name: str) -> List[Dict[str, Any]]:
        """获取领域的所有角色"""
        domain = self.get_domain(domain_name)
        return domain.get('roles', []) if domain else []

    def search_roles_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """根据关键词搜索角色"""
        results = []

        for domain_name, domain_data in self.domains.items():
            for role in domain_data.get('roles', []):
                # 搜索角色名称和职责
                if (keyword.lower() in role['role_name'].lower() or
                    any(keyword.lower() in resp.lower() for resp in role.get('responsibilities', []))):
                    results.append({
                        'domain': domain_name,
                        'role': role
                    })

        return results

    def save(self):
        """保存元库到文件"""
        library_file = Path(self.library_path) / "meta_library.json"
        save_json(self.domains, str(library_file))
        logger.info(f"Saved meta library to {library_file}")
