# HelloQoder

Qoder 编写的项目集合。

---

## 项目列表

| 项目 | 描述 | 技术栈 | 状态 |
|------|------|--------|------|
| [CartService](./CartService/) | 电商购物车微服务 | FastAPI, PostgreSQL, SQLAlchemy | Active |

---

## 目录结构

```
HelloQoder/
├── CartService/             # 购物车服务
│   ├── app/                 # 应用代码
│   ├── alembic/             # 数据库迁移
│   ├── Agent.md             # Agentic Coding 说明
│   ├── Agent&Chat.md        # Agentic Coding 过程
│   └── README.md            # 项目文档
├── <NewProject>/            # 后续新项目...
└── README.md                # 本文件
```

---

## 快速导航

### CartService

高性能电商购物车微服务，支持购物车 CRUD、商品管理、购物车合并等功能。

- **技术栈**: Python 3.10+ / FastAPI / PostgreSQL / SQLAlchemy 2.0
- **文档**: [查看详情](./CartService/README.md)

---

## 添加新项目

1. 在根目录下创建新项目文件夹
2. 添加项目代码和独立的 `README.md`
3. 可选：添加 `Agent.md` 和 `Agent&Chat.md`
4. 更新本文件的项目列表
