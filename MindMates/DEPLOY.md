# MindMates 部署文档

## 服务器要求

- **系统**: Ubuntu 22.04 64位
- **内存**: 最低 4GB，建议 8GB
- **存储**: 最低 20GB
- **网络**: 开放 80 端口

## 快速部署

### 1. 上传代码到服务器

```bash
# 方式1: 使用 scp
scp -r ./MindMates root@8.138.89.167:/opt/

# 方式2: 使用 git
ssh root@8.138.89.167
cd /opt
git clone <your-repo-url> MindMates
```

### 2. 配置环境变量

```bash
cd /opt/MindMates
cp .env.example .env
nano .env
```

**必须配置的变量:**
```
MIMO_API_KEY=你的MiMo API密钥
ZHIPU_API_KEY=你的智谱API密钥
JWT_SECRET=至少32位的随机字符串
```

### 3. 运行部署脚本

```bash
chmod +x deploy.sh
./deploy.sh
```

## 手动部署

如果自动脚本失败，可以手动执行:

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo systemctl enable docker
sudo systemctl start docker

# 启动服务
cd /opt/MindMates
docker compose up -d --build
```

## 服务管理

```bash
# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f

# 查看特定服务日志
docker compose logs -f backend-ai

# 重启服务
docker compose restart

# 停止服务
docker compose down

# 重新构建并启动
docker compose up -d --build
```

## 访问地址

| 服务 | 地址 |
|------|------|
| 前端 | http://8.138.89.167/ |
| 业务API | http://8.138.89.167/api/ |
| AI API | http://8.138.89.167/ai/ |
| 健康检查 | http://8.138.89.167/health |

## 数据库管理

PostgreSQL 数据持久化在 Docker Volume 中:

```bash
# 进入数据库容器
docker exec -it mindmates-postgres psql -U mindmates -d mindmates

# 备份数据库
docker exec mindmates-postgres pg_dump -U mindmates mindmates > backup.sql

# 恢复数据库
cat backup.sql | docker exec -i mindmates-postgres psql -U mindmates -d mindmates
```

## 故障排查

### 1. 容器启动失败

```bash
# 查看详细日志
docker compose logs backend-business
docker compose logs backend-ai
```

### 2. 数据库连接失败

```bash
# 检查 postgres 容器状态
docker compose ps postgres
docker compose logs postgres
```

### 3. API 无响应

```bash
# 检查 nginx 日志
docker compose logs nginx

# 检查各服务健康状态
curl http://localhost/health
```

## 更新部署

```bash
cd /opt/MindMates

# 拉取最新代码
git pull

# 重新构建并启动
docker compose up -d --build
```

## 安全建议

1. **修改默认密码**: 生产环境必须修改 `.env` 中的所有密码
2. **防火墙**: 只开放必要端口 (80, 443)
3. **HTTPS**: 建议使用 Let's Encrypt 配置 SSL
4. **备份**: 定期备份 PostgreSQL 数据
