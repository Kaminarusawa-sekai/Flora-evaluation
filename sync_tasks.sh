#!/bin/bash
# sync_tasks.sh - 同步 tasks 代码的脚本
#
# 使用方法:
#   ./sync_tasks.sh <source_path>
#
# 示例:
#   ./sync_tasks.sh /path/to/upstream/tasks
#   ./sync_tasks.sh git@github.com:your-org/tasks.git
#
# 此脚本会:
# 1. 备份当前的 tasks 目录（如果存在评估专用代码会警告）
# 2. 从源路径同步最新代码
# 3. 保留评估框架不受影响

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TASKS_DIR="$SCRIPT_DIR/tasks"
BACKUP_DIR="$SCRIPT_DIR/.tasks_backup"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查是否有评估专用代码残留在 tasks 中
check_eval_code_in_tasks() {
    local found=0

    if [ -f "$TASKS_DIR/capabilities/task_planning/mock_task_planning.py" ]; then
        log_warn "发现评估代码: tasks/capabilities/task_planning/mock_task_planning.py"
        found=1
    fi

    if [ -f "$TASKS_DIR/capabilities/excution/eval_execution.py" ]; then
        log_warn "发现评估代码: tasks/capabilities/excution/eval_execution.py"
        found=1
    fi

    if [ $found -eq 1 ]; then
        log_warn "建议删除 tasks 中的评估专用代码，使用 eval_extensions 代替"
    fi

    return $found
}

# 从本地路径同步
sync_from_local() {
    local source_path="$1"

    if [ ! -d "$source_path" ]; then
        log_error "源路径不存在: $source_path"
        exit 1
    fi

    log_info "从本地路径同步: $source_path"

    # 备份当前 tasks
    if [ -d "$TASKS_DIR" ]; then
        log_info "备份当前 tasks 到 $BACKUP_DIR"
        rm -rf "$BACKUP_DIR"
        cp -r "$TASKS_DIR" "$BACKUP_DIR"
    fi

    # 同步（排除 __pycache__ 和 .pyc）
    rsync -av --delete \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        "$source_path/" "$TASKS_DIR/"

    log_info "同步完成"
}

# 从 git 仓库同步
sync_from_git() {
    local git_url="$1"
    local branch="${2:-main}"
    local temp_dir=$(mktemp -d)

    log_info "从 Git 仓库同步: $git_url (branch: $branch)"

    # 克隆到临时目录
    git clone --depth 1 --branch "$branch" "$git_url" "$temp_dir/tasks"

    # 备份当前 tasks
    if [ -d "$TASKS_DIR" ]; then
        log_info "备份当前 tasks 到 $BACKUP_DIR"
        rm -rf "$BACKUP_DIR"
        cp -r "$TASKS_DIR" "$BACKUP_DIR"
    fi

    # 同步
    rsync -av --delete \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        "$temp_dir/tasks/" "$TASKS_DIR/"

    # 清理临时目录
    rm -rf "$temp_dir"

    log_info "同步完成"
}

# 主函数
main() {
    if [ $# -lt 1 ]; then
        echo "使用方法: $0 <source_path_or_git_url> [branch]"
        echo ""
        echo "示例:"
        echo "  $0 /path/to/upstream/tasks"
        echo "  $0 git@github.com:your-org/tasks.git main"
        exit 1
    fi

    local source="$1"
    local branch="${2:-main}"

    # 检查当前 tasks 中是否有评估代码
    if [ -d "$TASKS_DIR" ]; then
        check_eval_code_in_tasks || true
    fi

    # 判断是 git URL 还是本地路径
    if [[ "$source" == git@* ]] || [[ "$source" == https://* ]] || [[ "$source" == *.git ]]; then
        sync_from_git "$source" "$branch"
    else
        sync_from_local "$source"
    fi

    # 同步后再次检查
    log_info "检查同步后的代码..."
    check_eval_code_in_tasks || true

    log_info "完成！评估扩展位于 eval_extensions/ 目录"
}

main "$@"
