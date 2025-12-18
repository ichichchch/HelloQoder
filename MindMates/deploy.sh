#!/bin/bash
# =============================================================================
# MindMates 部署脚本
# Ubuntu 22.04 + Docker
# =============================================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# =============================================================================
# 1. 检查 Docker 是否安装
# =============================================================================
check_docker() {
    log_info "检查 Docker 安装状态..."
    
    if ! command -v docker &> /dev/null; then
        log_warn "Docker 未安装，开始安装..."
        install_docker
    else
        log_info "Docker 已安装: $(docker --version)"
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_warn "Docker Compose 未安装，开始安装..."
        install_docker_compose
    else
        log_info "Docker Compose 已安装"
    fi
}

# =============================================================================
# 2. 安装 Docker
# =============================================================================
install_docker() {
    log_info "安装 Docker..."
    
    # 更新包索引
    sudo apt-get update
    
    # 安装依赖
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release
    
    # 添加 Docker GPG 密钥
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # 设置仓库
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # 安装 Docker
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # 启动 Docker
    sudo systemctl start docker
    sudo systemctl enable docker
    
    # 将当前用户添加到 docker 组
    sudo usermod -aG docker $USER
    
    log_info "Docker 安装完成"
}

# =============================================================================
# 3. 安装 Docker Compose (如果需要)
# =============================================================================
install_docker_compose() {
    log_info "Docker Compose 已包含在 docker-compose-plugin 中"
}

# =============================================================================
# 4. 检查环境变量文件
# =============================================================================
check_env_file() {
    log_info "检查环境变量配置..."
    
    if [ ! -f ".env" ]; then
        if [ -f ".env.example" ]; then
            log_warn ".env 文件不存在，从 .env.example 复制..."
            cp .env.example .env
            log_error "请编辑 .env 文件，配置必要的 API Keys:"
            echo "  - MIMO_API_KEY"
            echo "  - ZHIPU_API_KEY"
            echo "  - JWT_SECRET"
            echo ""
            echo "编辑完成后，重新运行此脚本"
            exit 1
        else
            log_error ".env.example 文件不存在"
            exit 1
        fi
    fi
    
    # 检查必要的环境变量
    source .env
    
    if [ "$MIMO_API_KEY" == "your_mimo_api_key_here" ] || [ -z "$MIMO_API_KEY" ]; then
        log_error "请配置 MIMO_API_KEY"
        exit 1
    fi
    
    if [ "$ZHIPU_API_KEY" == "your_zhipu_api_key_here" ] || [ -z "$ZHIPU_API_KEY" ]; then
        log_error "请配置 ZHIPU_API_KEY"
        exit 1
    fi
    
    log_info "环境变量检查通过"
}

# =============================================================================
# 5. 构建和启动服务
# =============================================================================
deploy() {
    log_info "开始部署 MindMates..."
    
    # 停止旧容器
    log_info "停止旧容器..."
    docker compose down --remove-orphans 2>/dev/null || true
    
    # 构建镜像
    log_info "构建 Docker 镜像..."
    docker compose build --no-cache
    
    # 启动服务
    log_info "启动服务..."
    docker compose up -d
    
    # 等待服务启动
    log_info "等待服务启动..."
    sleep 10
    
    # 检查服务状态
    log_info "检查服务状态..."
    docker compose ps
    
    log_info "=========================================="
    log_info "部署完成!"
    log_info "=========================================="
    echo ""
    echo "访问地址: http://8.138.89.167"
    echo ""
    echo "API 端点:"
    echo "  - 前端: http://8.138.89.167/"
    echo "  - 业务API: http://8.138.89.167/api/"
    echo "  - AI API: http://8.138.89.167/ai/"
    echo ""
    echo "查看日志: docker compose logs -f"
    echo "停止服务: docker compose down"
    echo ""
}

# =============================================================================
# 6. 主函数
# =============================================================================
main() {
    echo "=========================================="
    echo "MindMates 部署脚本"
    echo "=========================================="
    echo ""
    
    # 进入项目目录
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    check_docker
    check_env_file
    deploy
}

# 运行主函数
main "$@"
