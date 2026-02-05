# api_server.py
"""
Flora多智能体协作系统 - API服务器实现（基于FastAPI）

FastAPI作为AgentActor的“翻译官”，将HTTP JSON请求转换为Python对象消息，
发送给Thespian ActorSystem，并将结果返回给用户。
"""

import logging
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid

# 导入Actor和消息定义

from common.messages.task_messages import AgentTaskMessage, ResumeTaskMessage
from capabilities import init_capabilities
from capabilities.registry import capability_registry
from agents.tree.tree_manager import treeManager

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Flora 多智能体协作系统 API",
    description="Flora系统的RESTful API接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _init_actor_system() -> None:
    """Lazy init ActorSystem to avoid heavy work at import time."""
    if getattr(app.state, "actor_system", None):
        return

    from thespian.actors import ActorSystem
    from agents.agent_actor import AgentActor

    app.state.actor_system = ActorSystem('simpleSystemBase')
    app.state.agent_actor_ref = app.state.actor_system.createActor(AgentActor)
    logger.info("ActorSystem initialized.")


def _ensure_actor_system() -> None:
    if not getattr(app.state, "actor_system", None):
        _init_actor_system()


def _ensure_capabilities_ready() -> None:
    missing = []
    for name in ("llm", "task_planning", "excution"):
        if not capability_registry.has_capability(name):
            missing.append(name)
    if missing:
        raise HTTPException(
            status_code=503,
            detail=f"Capabilities not ready: {', '.join(missing)}. Check tasks/config.json and API keys."
        )


@app.on_event("startup")
def _on_startup() -> None:
    init_capabilities()
    _init_actor_system()


@app.on_event("shutdown")
def _on_shutdown() -> None:
    actor_system = getattr(app.state, "actor_system", None)
    if actor_system:
        try:
            actor_system.shutdown()
        except Exception:
            logger.exception("Failed to shutdown ActorSystem cleanly.")

# --- 定义请求体模型 (Pydantic) ---
class TaskRequest(BaseModel):
    user_input: str
    user_id: str
    agent_id: str | None = None
    trace_id: str | None = None
    task_path: str | None = None

class ResumeRequest(BaseModel):
    task_id: str
    parameters: dict
    user_id: str
    trace_id: str | None = None
    task_path: str | None = None


def _get_default_agent_id() -> str:
    root_agents = treeManager.get_root_agents()
    return root_agents[0] if root_agents else "agent_root"


def _parse_user_id_payload(raw_user_id: str) -> tuple[str, dict]:
    """
    Parse user_id like "<userid:test_id,tenant_id:t_001>" into (user_id, params).
    """
    if not raw_user_id:
        return raw_user_id, {}

    text = raw_user_id.strip()
    if not (text.startswith("<") and text.endswith(">")):
        return raw_user_id, {}

    body = text[1:-1].strip()
    if not body:
        return raw_user_id, {}

    params = {}
    for part in body.split(","):
        chunk = part.strip()
        if not chunk or ":" not in chunk:
            continue
        key, value = chunk.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not key or not value:
            continue
        params[key] = value

    aliases = {
        "userid": "user_id",
        "userId": "user_id",
        "tenantId": "tenant_id",
        "tenantID": "tenant_id",
        "activeId": "active_id",
        "activeID": "active_id",
    }
    for alias, canonical in aliases.items():
        if alias in params and canonical not in params:
            params[canonical] = params[alias]

    user_id = params.get("user_id") or raw_user_id
    return user_id, params

# --- 核心接口 1: 执行任务 ---
@app.post("/tasks/execute")
def execute_task(req: TaskRequest):
    """
    执行新任务
    
    Args:
        req: 任务请求，包含用户输入和用户ID
        
    Returns:
        任务执行结果
    """
    try:
        _ensure_actor_system()
        _ensure_capabilities_ready()
        # 1. 生成唯一task_id
        task_id = str(uuid.uuid4())
        
        # 2. 构造Thespian消息
        trace_id = req.trace_id or task_id
        task_path = req.task_path or "/"
        agent_id = req.agent_id or _get_default_agent_id()

        user_id = req.user_id
        embedded_params = {}
        user_id, embedded_params = _parse_user_id_payload(req.user_id)
        if embedded_params and "user_id" not in embedded_params:
            embedded_params["user_id"] = user_id

        msg = AgentTaskMessage(
            content=req.user_input,
            description=req.user_input,
            user_id=user_id,
            task_id=task_id,
            trace_id=trace_id,
            task_path=task_path,
            agent_id=agent_id,
            parameters=embedded_params,
        )
        
        # 3. 发送给Actor并等待回复（同步阻塞）
        # timeout设为60秒，因为LLM处理可能较慢
        response = app.state.actor_system.ask(app.state.agent_actor_ref, msg, timeout=60)
        
        if response is None:
            raise HTTPException(status_code=504, detail="Agent processing timeout")
        
        # 4. 返回结果给前端
        return {
            "success": True,
            "data": response,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error executing task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": str(e)
            }
        )

# --- 核心接口 2: 补充参数/恢复任务 ---
@app.post("/tasks/resume")
def resume_task(req: ResumeRequest):
    """
    恢复任务并补充参数
    
    Args:
        req: 恢复请求，包含任务ID、补充参数和用户ID
        
    Returns:
        任务执行结果
    """
    try:
        _ensure_actor_system()
        _ensure_capabilities_ready()
        # 1. 构造Thespian消息
        trace_id = req.trace_id or req.task_id
        task_path = req.task_path or "/"

        msg = ResumeTaskMessage(
            task_id=req.task_id,
            parameters=req.parameters,
            user_id=req.user_id,
            trace_id=trace_id,
            task_path=task_path
        )
        
        # 2. 发送给Actor并等待回复
        response = app.state.actor_system.ask(app.state.agent_actor_ref, msg, timeout=60)
        
        if response is None:
            raise HTTPException(status_code=504, detail="Agent processing timeout")
        
        # 3. 返回结果给前端
        return {
            "success": True,
            "data": response,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error resuming task: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": str(e)
            }
        )

# --- 健康检查端点 ---
@app.get("/health")
def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "flora-api-server"
    }

# --- 核心接口 3: 获取Agent子树 ---
@app.get("/agents/tree/subtree/{root_id}")
def get_agent_subtree(root_id: str):
    """
    获取以指定节点为根的Agent子树
    
    Args:
        root_id: 根节点Agent ID
        
    Returns:
        子树结构，格式如下：
        {
            "agent_id": str,              # 节点Agent ID
            "meta": {                     # 节点元数据
                "name": str,              # Agent名称
                "type": str,              # Agent类型
                "is_leaf": bool,          # 是否为叶子节点
                "weight": float,          # 权重值
                "description": str        # 描述信息
                # 其他元数据字段...
            },
            "children": [                 # 子节点列表（递归结构）
                {
                    "agent_id": str,
                    "meta": {},
                    "children": [...]
                }
                # 更多子节点...
            ]
        }
    """
    try:
        subtree = treeManager.get_subtree(root_id)
        if not subtree:
            raise HTTPException(status_code=404, detail=f"Agent {root_id} not found")
        
        return {
            "success": True,
            "data": subtree,
            "error": None
        }
    except Exception as e:
        logger.error(f"Error getting subtree for agent {root_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "success": False,
                "data": None,
                "error": str(e)
            }
        )


# 工厂函数，用于创建API服务器实例
def create_api_server(config: dict = None) -> FastAPI:
    """
    创建API服务器实例
    
    Args:
        config: 服务器配置
        
    Returns:
        FastAPI应用实例
    """
    return app


# 如果直接运行此文件，则启动服务器
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Flora API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Run in debug mode')
    
    args = parser.parse_args()
    
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info(f"Starting API server on {args.host}:{args.port}")
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.debug
    )
