# Cart Service

高性能电商购物车微服务，基于 Python + FastAPI + PostgreSQL 构建。

- **开发过程记录**: [Agent&Chat.md](./docs/Agent&Chat.md)

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 运行环境 |
| FastAPI | 0.109+ | 高性能异步 Web 框架 |
| PostgreSQL | 15+ | 关系型数据库 |
| SQLAlchemy | 2.0+ | 异步 ORM |
| Pydantic | v2 | 数据验证 |
| Alembic | 1.13+ | 数据库迁移 |

## 项目结构

```
cart-service/
├── app/
│   ├── api/v1/endpoints/    # API 路由层
│   ├── core/                # 配置管理
│   ├── db/                  # 数据库连接
│   ├── models/              # ORM 模型
│   ├── schemas/             # Pydantic 模型
│   ├── services/            # 业务逻辑层
│   └── main.py              # 应用入口
├── alembic/                 # 数据库迁移脚本
├── .env.example             # 环境变量模板
├── alembic.ini              # Alembic 配置
└── requirements.txt         # 依赖清单
```

## 快速开始

### 1. 安装依赖

```bash
cd projects/cart-service
pip install -r requirements.txt
```

### 2. 配置数据库

创建 PostgreSQL 数据库：

```sql
CREATE DATABASE cart_db;
```

配置环境变量：

```bash
copy .env.example .env
# 编辑 .env 文件，设置正确的数据库连接信息
```

### 3. 数据库迁移

```bash
alembic upgrade head
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload
```

### 5. 访问 API

- **Swagger 文档**: http://127.0.0.1:8000/docs
- **ReDoc 文档**: http://127.0.0.1:8000/redoc
- **健康检查**: http://127.0.0.1:8000/health

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/v1/carts/{cart_id}` | 获取购物车详情 |
| POST | `/api/v1/carts` | 创建购物车 |
| POST | `/api/v1/carts/{cart_id}/items` | 添加商品 |
| PATCH | `/api/v1/carts/{cart_id}/items/{item_id}` | 更新商品数量 |
| DELETE | `/api/v1/carts/{cart_id}/items/{item_id}` | 移除商品 |
| DELETE | `/api/v1/carts/{cart_id}` | 清空购物车 |
| POST | `/api/v1/carts/{cart_id}/merge` | 合并购物车 |

## 数据模型

### carts 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 用户 ID (可为空) |
| status | VARCHAR | 状态 |
| created_at | DATETIME | 创建时间 |
| updated_at | DATETIME | 更新时间 |

### cart_items 表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| cart_id | UUID | 购物车 ID |
| product_id | VARCHAR | 商品 SKU |
| quantity | INTEGER | 数量 |
| unit_price | DECIMAL | 单价 |
| added_at | DATETIME | 添加时间 |
