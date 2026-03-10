"""
自动提示词优化 Web API 服务
提供REST API接口用于提示词优化
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging
from enum import Enum

from config import APOConfig, Task
from optimizer import PromptOptimizer
from utils import ResultSaver

# ==========================================
# 数据模型定义
# ==========================================

class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"      # 等待中
    RUNNING = "running"      # 运行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败


class Example(BaseModel):
    """训练样本"""
    input: str = Field(..., description="输入文本")
    output: str = Field(..., description="期望输出")

    # 分层提示词支持（可选）
    dynamic_context: Optional[str] = Field(None, description="动态上下文（可选）")
    dynamic_examples: Optional[List[Dict[str, Any]]] = Field(None, description="动态示例（可选）")


class OptimizationRequest(BaseModel):
    """优化请求"""
    # 任务定义
    task_name: str = Field(..., description="任务名称", example="情感分析")
    task_description: str = Field(..., description="任务描述", example="判断文本情感是积极还是消极")

    # 数据
    examples: List[Example] = Field(..., description="训练样本（至少3个）", min_items=3)
    validation_data: List[Example] = Field(..., description="验证样本（至少3个）", min_items=3)

    # 初始提示词（必填！）
    initial_prompts: List[str] = Field(..., description="你的初始提示词（1-5个）", min_items=1, max_items=5)

    # 分层提示词配置（可选，方案4）
    core_instruction: Optional[str] = Field(None, description="核心指令（待优化部分），不设置则使用task_description")
    context_template: Optional[str] = Field(None, description="上下文模板，如：'参考信息：{context}'")
    example_template: Optional[str] = Field(None, description="示例模板，如：'示例{index}: Q: {input} A: {output}'")
    prompt_structure: Optional[List[str]] = Field(None, description="提示词结构顺序，如：['core', 'context', 'examples', 'input']")

    # 优化配置（可选）
    max_iterations: int = Field(default=10, ge=1, le=50, description="最大迭代次数")
    num_candidates: int = Field(default=5, ge=2, le=10, description="每轮生成的候选数")
    top_k: int = Field(default=3, ge=1, le=5, description="保留的最优候选数")
    early_stop_threshold: float = Field(default=0.95, ge=0.0, le=1.0, description="早停阈值")

    # 快速测试模式（用于接口测试）
    fast_mode: bool = Field(default=False, description="快速测试模式（禁用数据增强，减少迭代）")
    auto_augment_data: bool = Field(default=True, description="是否自动增强验证数据")

    class Config:
        json_schema_extra = {
            "example": {
                "task_name": "情感分析",
                "task_description": "判断文本情感是积极还是消极",
                "examples": [
                    {"input": "这个产品很棒", "output": "positive"},
                    {"input": "质量太差了", "output": "negative"},
                    {"input": "非常满意", "output": "positive"}
                ],
                "validation_data": [
                    {"input": "服务很好", "output": "positive"},
                    {"input": "太贵了", "output": "negative"},
                    {"input": "值得推荐", "output": "positive"}
                ],
                "initial_prompts": [
                    "请判断以下文本的情感是positive还是negative"
                ],
                "max_iterations": 10
            }
        }


class OptimizationResponse(BaseModel):
    """优化响应"""
    task_id: str = Field(..., description="任务ID，用于查询结果")
    status: TaskStatus = Field(..., description="任务状态")
    message: str = Field(..., description="提示信息")
    created_at: str = Field(..., description="创建时间")


class OptimizationResult(BaseModel):
    """优化结果"""
    task_id: str
    status: TaskStatus

    # 结果数据
    best_prompt: Optional[str] = None
    best_score: Optional[float] = None
    initial_score: Optional[float] = None
    improvement: Optional[float] = None
    iterations: Optional[int] = None

    # 优化历史
    score_history: Optional[List[float]] = None

    # 错误信息
    error: Optional[str] = None

    # 时间信息
    created_at: str
    completed_at: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "healthy"
    version: str = "1.0.0"
    api_key_configured: bool


# ==========================================
# 全局状态管理
# ==========================================

# 存储所有任务的状态和结果
tasks_storage: Dict[str, Dict[str, Any]] = {}

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==========================================
# FastAPI应用
# ==========================================

app = FastAPI(
    title="自动提示词优化 API",
    description="提供提示词自动优化服务的REST API",
    version="1.0.0",
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc"  # ReDoc
)

# 配置CORS（允许跨域）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================
# 后台任务执行函数
# ==========================================

def run_optimization_task(task_id: str, request: OptimizationRequest):
    """在后台执行优化任务"""
    try:
        logger.info(f"开始执行任务 {task_id}")

        # 更新状态为运行中
        tasks_storage[task_id]["status"] = TaskStatus.RUNNING

        # 转换examples和validation_data（包含分层提示词的字段）
        def convert_example(ex: Example) -> Dict[str, Any]:
            """转换Example对象为字典，包含分层提示词字段"""
            result = {"input": ex.input, "output": ex.output}
            if ex.dynamic_context:
                result["dynamic_context"] = ex.dynamic_context
            if ex.dynamic_examples:
                result["dynamic_examples"] = ex.dynamic_examples
            return result

        examples = [convert_example(ex) for ex in request.examples]
        validation_data = [convert_example(ex) for ex in request.validation_data]

        # 创建任务定义（支持分层提示词）
        task = Task(
            name=request.task_name,
            description=request.task_description,
            examples=examples,
            validation_data=validation_data,
            core_instruction=request.core_instruction,
            context_template=request.context_template,
            example_template=request.example_template,
            prompt_structure=request.prompt_structure,
        )

        # 快速模式优化配置
        if request.fast_mode:
            logger.info("⚡ 使用快速测试模式")
            config = APOConfig(
                max_iterations=min(request.max_iterations, 3),  # 最多3次迭代
                num_candidates=min(request.num_candidates, 2),  # 最多2个候选
                top_k=1,
                generation_strategy="mutation",  # 使用简单变异
                use_llm_feedback=False,
                early_stop_threshold=0.80,
                verbose=True,
            )
            target_validation_size = len(request.validation_data)  # 不扩展数据
        else:
            # 正常模式配置
            config = APOConfig(
                max_iterations=request.max_iterations,
                num_candidates=request.num_candidates,
                top_k=request.top_k,
                early_stop_threshold=request.early_stop_threshold,
                generation_strategy="llm_rewrite",
                use_llm_feedback=True,
                verbose=True,
            )
            target_validation_size = 30

        # 创建优化器
        optimizer = PromptOptimizer(config, task)

        # 执行优化（使用用户提供的初始提示词）
        result = optimizer.optimize(
            initial_prompts=request.initial_prompts,
            auto_augment_data=request.auto_augment_data and not request.fast_mode,
            target_validation_size=target_validation_size
        )

        # 保存结果
        tasks_storage[task_id].update({
            "status": TaskStatus.COMPLETED,
            "best_prompt": result["best_prompt"],
            "best_score": result["best_score"],
            "initial_score": result["initial_score"],
            "improvement": result["improvement"],
            "iterations": result["iterations"],
            "score_history": result["history"]["best_scores"],
            "completed_at": datetime.now().isoformat(),
        })

        # 保存到文件
        ResultSaver.save_optimization_result(result, f"results/api_task_{task_id}.json")

        logger.info(f"任务 {task_id} 完成，最佳分数: {result['best_score']}")

    except Exception as e:
        logger.error(f"任务 {task_id} 失败: {str(e)}")
        tasks_storage[task_id].update({
            "status": TaskStatus.FAILED,
            "error": str(e),
            "completed_at": datetime.now().isoformat(),
        })


# ==========================================
# API 端点
# ==========================================

@app.get("/", tags=["健康检查"])
async def root():
    """根路径，返回API信息"""
    return {
        "name": "自动提示词优化 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse, tags=["健康检查"])
async def health_check():
    """健康检查"""
    import os
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        api_key_configured=bool(os.getenv("QWEN_API_KEY"))
    )


@app.post("/optimize", response_model=OptimizationResponse, tags=["优化"])
async def create_optimization_task(
    request: OptimizationRequest,
    background_tasks: BackgroundTasks
):
    """
    创建提示词优化任务

    提交优化请求后会立即返回task_id，然后在后台执行优化。
    使用task_id查询优化状态和结果。
    """
    # 生成任务ID
    task_id = str(uuid.uuid4())

    # 初始化任务状态
    tasks_storage[task_id] = {
        "task_id": task_id,
        "status": TaskStatus.PENDING,
        "created_at": datetime.now().isoformat(),
        "request": request.model_dump(),
    }

    # 添加后台任务
    background_tasks.add_task(run_optimization_task, task_id, request)

    logger.info(f"创建优化任务: {task_id}")

    return OptimizationResponse(
        task_id=task_id,
        status=TaskStatus.PENDING,
        message="优化任务已创建，正在后台执行",
        created_at=tasks_storage[task_id]["created_at"]
    )


@app.get("/status/{task_id}", response_model=OptimizationResult, tags=["查询"])
async def get_task_status(task_id: str):
    """
    查询任务状态

    返回任务的当前状态和结果（如果已完成）
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务不存在")

    task_data = tasks_storage[task_id]

    return OptimizationResult(
        task_id=task_id,
        status=task_data["status"],
        best_prompt=task_data.get("best_prompt"),
        best_score=task_data.get("best_score"),
        initial_score=task_data.get("initial_score"),
        improvement=task_data.get("improvement"),
        iterations=task_data.get("iterations"),
        score_history=task_data.get("score_history"),
        error=task_data.get("error"),
        created_at=task_data["created_at"],
        completed_at=task_data.get("completed_at"),
    )


@app.get("/result/{task_id}", response_model=OptimizationResult, tags=["查询"])
async def get_task_result(task_id: str):
    """
    获取任务结果

    只有任务完成后才会返回结果，否则返回状态信息
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务不存在")

    task_data = tasks_storage[task_id]

    if task_data["status"] == TaskStatus.PENDING:
        raise HTTPException(status_code=202, detail="任务等待中，请稍后查询")
    elif task_data["status"] == TaskStatus.RUNNING:
        raise HTTPException(status_code=202, detail="任务运行中，请稍后查询")
    elif task_data["status"] == TaskStatus.FAILED:
        raise HTTPException(status_code=500, detail=f"任务失败: {task_data.get('error')}")

    return OptimizationResult(
        task_id=task_id,
        status=task_data["status"],
        best_prompt=task_data["best_prompt"],
        best_score=task_data["best_score"],
        initial_score=task_data["initial_score"],
        improvement=task_data["improvement"],
        iterations=task_data["iterations"],
        score_history=task_data.get("score_history"),
        created_at=task_data["created_at"],
        completed_at=task_data["completed_at"],
    )


@app.get("/tasks", tags=["查询"])
async def list_tasks():
    """
    列出所有任务

    返回所有任务的概览信息
    """
    return {
        "total": len(tasks_storage),
        "tasks": [
            {
                "task_id": task_id,
                "status": task_data["status"],
                "created_at": task_data["created_at"],
                "task_name": task_data["request"]["task_name"],
            }
            for task_id, task_data in tasks_storage.items()
        ]
    }


@app.delete("/task/{task_id}", tags=["管理"])
async def delete_task(task_id: str):
    """
    删除任务记录
    """
    if task_id not in tasks_storage:
        raise HTTPException(status_code=404, detail="任务不存在")

    del tasks_storage[task_id]
    return {"message": f"任务 {task_id} 已删除"}


# ==========================================
# 启动服务
# ==========================================

if __name__ == "__main__":
    import uvicorn
    import os

    # 确保results目录存在
    os.makedirs("results", exist_ok=True)

    print("\n" + "="*70)
    print("🚀 自动提示词优化 API 服务启动")
    print("="*70)
    print("\n📖 API文档地址:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc:      http://localhost:8000/redoc")
    print("\n🔧 健康检查:")
    print("  - GET http://localhost:8000/health")
    print("\n💡 主要端点:")
    print("  - POST   http://localhost:8000/optimize       创建优化任务")
    print("  - GET    http://localhost:8000/status/{id}    查询任务状态")
    print("  - GET    http://localhost:8000/result/{id}    获取优化结果")
    print("  - GET    http://localhost:8000/tasks          列出所有任务")
    print("\n" + "="*70 + "\n")

    # 启动服务
    uvicorn.run(
        app,
        host="0.0.0.0",  # 允许外部访问
        port=8100,
        log_level="info"
    )
