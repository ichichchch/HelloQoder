# AI Agent Guide: E-commerce Shopping Cart Backend

这份文档旨在为 AI 助手提供关于本项目（电商购物车后端服务）的上下文、技术栈约束和开发规范。请在生成代码、重构或回答问题时严格遵循以下指南。

## 1. 项目概述 (Project Overview)
本项目是一个基于 Python 的高性能电商购物车微服务。
- **核心功能**：管理用户的购物车会话，包括添加商品、更新数量、移除商品、计算总价、持久化存储。
- **业务特点**：支持匿名用户（基于 Session/Device ID）和登录用户；高并发读写；数据强一致性。

## [...](asc_slot://start-slot-4)2. 技术栈 (Tech Stack)
请严格使用以下指定的版本和库：
- **编程语言**: Python 3.10+
- **Web 框架**: FastAPI (最新稳定版)
- **数据库**: PostgreSQL 15+
- **ORM / 数据库驱动**:
  - `SQLAlchemy` 2.0+ (必须使用 **Async** 模式)
  - `asyncpg` (作为底层驱动)
  - `Alembic` (用于数据库迁移)
- **数据验证**: Pydantic v2
- **依赖管理**: Poetry 或 pip (requirements.txt)

## 3. 数据库设计 (Database Schema)
购物车模块主要涉及两张表。AI 在生成 SQL 或 Model 时应遵循此设计：

### 3.1 `carts` 表 (购物车主表)
| 字段名 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | 购物车唯一标识 |
| `user_id` | UUID | Nullable, Index | 关联用户 ID (未登录为空) |
| `status` | VARCHAR | Default 'active' | 状态: active, merged, abandoned, converted |
| `created_at` | DATETIME | Not Null | 创建时间 |
| `updated_at` | DATETIME | Not Null | 更新时间 |

### 3.2 `cart_items` 表 (购物车明细表)
| 字段名 | 类型 | 约束 | 说明 |
| :--- | :--- | :--- | :--- |
| `id` | UUID | PK | 明细项 ID |
| `cart_id` | UUID | FK -> carts.id | 关联购物车 |
| `product_id` | VARCHAR | Not Null | 商品 SKU ID |
| `quantity` | INTEGER | Check > 0 | 购买数量 |
| `unit_price` | DECIMAL | Not Null | 加入时的单价 (用于价格快照/变动提醒) |
| `added_at` | DATETIME | Not Null | 加入时间 |

*约束*: `(cart_id, product_id)` 应建立联合唯一索引，避免重复行。

## 4. API 接口规范 (API Specification)
所有接口应遵循 RESTful 风格，路径前缀 `/api/v1`。

- **GET** `/carts/{cart_id}`
  - 获取购物车详情（包含所有商品项和计算后的总价）。
- **POST** `/carts`
  - 创建新购物车（通常在添加第一个商品时隐式调用，或显式初始化）。
- **POST** `/carts/{cart_id}/items`
  - 添加商品。如果商品已存在，则增加数量。
  - Body: `{ "product_id": "...", "quantity": 1 }`
- **PATCH** `/carts/{cart_id}/items/{item_id}`
  - 更新商品数量。
  - Body: `{ "quantity": 5 }`
- **DELETE** `/carts/{cart_id}/items/{item_id}`
  - 移除单个商品。
- **DELETE** `/carts/{cart_id}`
  - 清空购物车。
- **POST** `/carts/{cart_id}/merge`
  - (可选) 用户登录后，将匿名购物车合并到用户购物车。

## 5. [...](asc_slot://start-slot-6)代码开发规范 (Coding Standards)

### 5.1 异步优先 (Async First)
- 所有 I/O 操作（数据库查询、HTTP 请求）**必须**使用 `async/await`。
- FastAPI 路径操作函数定义为 `async def`。

### 5.2 类型提示 (Type Hinting)
- 必须使用 Python 类型提示。
- 返回类型应使用 Pydantic Model 进行定义，例如 `response_model=CartSchema`。

### 5.3 错误处理 (Error Handling)
- 使用 FastAPI 的 `HTTPException` 抛出错误。
- 常见错误码：
  - `404 Not Found`: 购物车或商品不存在。
  - `400 Bad Request`: 库存不足或参数错误。
  - `401 Unauthorized`: 越权访问他人购物车。

### [...](asc_slot://start-slot-8)5.4 目录结构 (Directory Structure)
```text
app/
├── api/
│   ├── v1/
│   │   └── endpoints/
│   │       └── cart.py    # 路由层
├── core/                  # 配置、安全、常量
├── db/                    # 数据库连接 session
├── models/                # SQLAlchemy ORM 模型
│   └── cart.py
├── schemas/               # Pydantic 数据模型 (Request/Response)
│   └── cart.py
├── services/              # 业务逻辑层 (CRUD 操作)
│   └── cart_service.py
└── main.py
