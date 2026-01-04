# Cart Service

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**High-Performance E-commerce Shopping Cart Microservice**

*Based on FastAPI + SQLAlchemy 2.0 async architecture, supporting full shopping cart lifecycle management*

English | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Development Log**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Features

- 🛒 **Cart Management** - Create, query, and clear shopping carts
- 📦 **Item Operations** - Add, update quantity, and remove items
- 🔄 **Cart Merge** - Support merging anonymous cart with user cart
- ⚡ **Async Architecture** - High-performance design based on async/await
- 📊 **Price Snapshot** - Record unit price when item is added

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime Environment |
| FastAPI | 0.109+ | High-performance Async Web Framework |
| PostgreSQL | 15+ | Relational Database |
| SQLAlchemy | 2.0+ | Async ORM |
| Pydantic | v2 | Data Validation |
| Alembic | 1.13+ | Database Migration |

---

## 🏗️ Project Structure

```
cart-service/
├── app/
│   ├── api/v1/endpoints/    # API Routes
│   ├── core/                # Configuration Management
│   ├── db/                  # Database Connection
│   ├── models/              # ORM Models
│   ├── schemas/             # Pydantic Models
│   ├── services/            # Business Logic Layer
│   └── main.py              # Application Entry
├── alembic/                 # Database Migration Scripts
├── .env.example             # Environment Variables Template
├── alembic.ini              # Alembic Configuration
└── requirements.txt         # Dependencies
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd projects/cart-service
pip install -r requirements.txt
```

### 2. Configure Database

Create PostgreSQL database:

```sql
CREATE DATABASE cart_db;
```

Configure environment variables:

```bash
copy .env.example .env
# Edit .env file and set correct database connection info
```

### 3. Database Migration

```bash
alembic upgrade head
```

### 4. Start Service

```bash
uvicorn app.main:app --reload
```

### 5. Access API

- **Swagger Docs**: http://127.0.0.1:8000/docs
- **ReDoc Docs**: http://127.0.0.1:8000/redoc
- **Health Check**: http://127.0.0.1:8000/health

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/carts/{cart_id}` | Get cart details |
| POST | `/api/v1/carts` | Create cart |
| POST | `/api/v1/carts/{cart_id}/items` | Add item |
| PATCH | `/api/v1/carts/{cart_id}/items/{item_id}` | Update item quantity |
| DELETE | `/api/v1/carts/{cart_id}/items/{item_id}` | Remove item |
| DELETE | `/api/v1/carts/{cart_id}` | Clear cart |
| POST | `/api/v1/carts/{cart_id}/merge` | Merge carts |

---

## 🗃️ Data Models

### carts Table

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary Key |
| user_id | UUID | User ID (nullable) |
| status | VARCHAR | Status |
| created_at | DATETIME | Creation Time |
| updated_at | DATETIME | Update Time |

### cart_items Table

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary Key |
| cart_id | UUID | Cart ID |
| product_id | VARCHAR | Product SKU |
| quantity | INTEGER | Quantity |
| unit_price | DECIMAL | Unit Price |
| added_at | DATETIME | Added Time |

---

## 📖 Development Documentation

- [AI Agent Development Guide](./Agent.md) - Tech stack constraints and development standards

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Made with ❤️ using Python and FastAPI**

</div>
