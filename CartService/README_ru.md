# Cart Service

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Высокопроизводительный микросервис корзины покупок для e-commerce**

*На основе асинхронной архитектуры FastAPI + SQLAlchemy 2.0, поддержка полного жизненного цикла корзины*

[English](./README.md) | [中文](./README_zh.md) | Русский | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Журнал разработки**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Возможности

- 🛒 **Управление корзиной** - Создание, просмотр, очистка корзин
- 📦 **Операции с товарами** - Добавление, обновление количества, удаление товаров
- 🔄 **Слияние корзин** - Поддержка слияния анонимной корзины с пользовательской
- ⚡ **Асинхронная архитектура** - Высокопроизводительный дизайн на async/await
- 📊 **Снимок цены** - Сохранение цены товара на момент добавления

---

## 🛠️ Технологии

| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.10+ | Среда выполнения |
| FastAPI | 0.109+ | Высокопроизводительный асинхронный веб-фреймворк |
| PostgreSQL | 15+ | Реляционная база данных |
| SQLAlchemy | 2.0+ | Асинхронный ORM |
| Pydantic | v2 | Валидация данных |
| Alembic | 1.13+ | Миграция базы данных |

---

## 🏗️ Структура проекта

```
cart-service/
├── app/
│   ├── api/v1/endpoints/    # API маршруты
│   ├── core/                # Управление конфигурацией
│   ├── db/                  # Подключение к БД
│   ├── models/              # ORM модели
│   ├── schemas/             # Pydantic модели
│   ├── services/            # Бизнес-логика
│   └── main.py              # Точка входа
├── alembic/                 # Скрипты миграции БД
├── .env.example             # Шаблон переменных окружения
├── alembic.ini              # Конфигурация Alembic
└── requirements.txt         # Зависимости
```

---

## 🚀 Быстрый старт

### 1. Установка зависимостей

```bash
cd projects/cart-service
pip install -r requirements.txt
```

### 2. Настройка базы данных

Создайте базу данных PostgreSQL:

```sql
CREATE DATABASE cart_db;
```

Настройте переменные окружения:

```bash
copy .env.example .env
# Отредактируйте файл .env и установите правильные параметры подключения к БД
```

### 3. Миграция базы данных

```bash
alembic upgrade head
```

### 4. Запуск сервиса

```bash
uvicorn app.main:app --reload
```

### 5. Доступ к API

- **Swagger документация**: http://127.0.0.1:8000/docs
- **ReDoc документация**: http://127.0.0.1:8000/redoc
- **Проверка состояния**: http://127.0.0.1:8000/health

---

## 📡 API Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/v1/carts/{cart_id}` | Получение деталей корзины |
| POST | `/api/v1/carts` | Создание корзины |
| POST | `/api/v1/carts/{cart_id}/items` | Добавление товара |
| PATCH | `/api/v1/carts/{cart_id}/items/{item_id}` | Обновление количества |
| DELETE | `/api/v1/carts/{cart_id}/items/{item_id}` | Удаление товара |
| DELETE | `/api/v1/carts/{cart_id}` | Очистка корзины |
| POST | `/api/v1/carts/{cart_id}/merge` | Слияние корзин |

---

## 🗃️ Модели данных

### Таблица carts

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | Первичный ключ |
| user_id | UUID | ID пользователя (может быть null) |
| status | VARCHAR | Статус |
| created_at | DATETIME | Время создания |
| updated_at | DATETIME | Время обновления |

### Таблица cart_items

| Поле | Тип | Описание |
|------|-----|----------|
| id | UUID | Первичный ключ |
| cart_id | UUID | ID корзины |
| product_id | VARCHAR | SKU товара |
| quantity | INTEGER | Количество |
| unit_price | DECIMAL | Цена за единицу |
| added_at | DATETIME | Время добавления |

---

## 📖 Документация разработки

- [Руководство разработки AI Agent](./Agent.md) - Ограничения технологического стека и стандарты разработки

---

## 📄 Лицензия

Этот проект лицензирован под MIT License.

---

<div align="center">

**Made with ❤️ using Python and FastAPI**

</div>
