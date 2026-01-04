# MindMates

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Платформа AI-компаньона для психологического здоровья**

*Круглосуточные интеллектуальные психологические консультации на основе Xiaomi MiMo LLM*

[English](./README.md) | [中文](./README_zh.md) | Русский | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Журнал разработки**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Возможности

- ✅ Интеллектуальный психологический диалог на основе MiMo LLM
- ✅ RAG-расширенные ответы по профессиональным знаниям психологии
- ✅ Автоматическое обнаружение кризисных ситуаций и рекомендации ресурсов помощи
- ✅ Память контекста многораундовых диалогов
- ✅ История и управление сессиями
- ✅ Система JWT аутентификации пользователей
- ✅ Кроссплатформенная мобильная поддержка Capacitor (iOS/Android)
- ✅ Развертывание одной командой через Docker Compose

---

## 🛠️ Технологии

| Уровень | Технология | Версия |
|---------|------------|--------|
| Frontend фреймворк | Vue + TypeScript + Vite | 3.5+ |
| UI компоненты | Element Plus + Tailwind CSS | 2.9+ / 3.4+ |
| Мобильный рантайм | Capacitor | 7.0+ |
| Бизнес-бэкенд | .NET + Entity Framework Core | 10 |
| AI бэкенд | Python + FastAPI + LangChain | 3.13 / 0.115+ |
| AI модель | Xiaomi MiMo-V2-Flash | - |
| База данных | PostgreSQL | 17 |
| Векторная БД | Milvus | 2.4+ |
| Развертывание | Docker Compose + Nginx | - |

---

## 🚀 Быстрый старт

### 1. Требования

- Node.js 20+
- .NET 10 SDK
- Python 3.13+
- PostgreSQL 17

### 2. Запуск одной командой

```bash
# Windows - Запуск всех сервисов
.\start-all.bat

# Или запустить по отдельности
.\start-frontend.bat       # http://localhost:5173
.\start-backend-business.bat  # http://localhost:5000
.\start-backend-ai.bat     # http://localhost:8000
```

### 3. Docker развертывание

```bash
# Настройка переменных окружения
cp .env.example .env

# Запуск всех сервисов
docker compose up -d
```

---

## 🏗️ Структура проекта

```
MindMates/
├── frontend/                 # Vue 3 Frontend приложение
│   ├── src/
│   │   ├── api/             # API клиент
│   │   ├── views/           # Компоненты страниц
│   │   ├── stores/          # Pinia управление состоянием
│   │   └── router/          # Конфигурация маршрутов
│   └── capacitor.config.ts  # Мобильная конфигурация
│
├── backend-business/         # .NET бизнес-бэкенд (Clean Architecture)
│   ├── MindMates.Api/       # API слой
│   ├── MindMates.Application/ # Слой приложения
│   ├── MindMates.Domain/    # Доменный слой
│   └── MindMates.Infrastructure/ # Инфраструктурный слой
│
└── backend-ai/              # Python AI бэкенд
    ├── app/
    │   ├── memory/          # Система памяти диалогов
    │   ├── services/        # Сервисы чата
    │   ├── llm.py           # Интеграция MiMo LLM
    │   ├── rag.py           # Сервис RAG извлечения
    │   └── crisis_detector.py # Обнаружение кризисов
    └── main.py              # Точка входа FastAPI
```

---

## ⚙️ Конфигурация

### Конфигурация Frontend (`frontend/.env`)

```env
VITE_API_URL=http://localhost:5000
VITE_AI_API_URL=http://localhost:8000
```

### Конфигурация бизнес-бэкенда (`backend-business/appsettings.json`)

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=mindmates;Username=..."
  },
  "Jwt": {
    "Secret": "your-secret-key-at-least-32-characters",
    "Issuer": "MindMates",
    "Audience": "MindMates"
  }
}
```

### Конфигурация AI бэкенда (`backend-ai/.env`)

```env
MIMO_API_KEY=your_mimo_api_key
MIMO_API_BASE=https://api.xiaomimimo.com/v1
ZHIPU_API_KEY=your_zhipu_api_key
```

---

## 📡 API Эндпоинты

### API аутентификации (бизнес-бэкенд)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/auth/register` | Регистрация пользователя |
| POST | `/api/auth/login` | Вход пользователя |
| GET | `/api/auth/profile` | Получение информации о пользователе |
| PUT | `/api/auth/profile` | Обновление информации о пользователе |

### API чата (бизнес-бэкенд)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/chat/sessions` | Получение списка сессий |
| POST | `/api/chat/sessions` | Создание новой сессии |
| GET | `/api/chat/sessions/:id/messages` | Получение истории сообщений |
| POST | `/api/chat/sessions/:id/messages` | Отправка сообщения |

### AI API (AI бэкенд)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/chat` | AI интерфейс чата |
| GET | `/health` | Проверка состояния |

---

## 📊 Архитектура системы

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend  │────▶│  Backend-Business │────▶│   Backend-AI    │
│  Vue 3 SPA  │     │   .NET 10 API    │     │ FastAPI + MiMo  │
└─────────────┘     └──────────────────┘     └─────────────────┘
                            │                        │
                            ▼                        ▼
                    ┌──────────────┐         ┌─────────────┐
                    │  PostgreSQL  │         │   Milvus    │
                    └──────────────┘         └─────────────┘
```

---

## ⚠️ Уведомление о психологическом здоровье

> Если вы испытываете серьезные психологические трудности, пожалуйста, немедленно обратитесь за профессиональной помощью.
> 
> **Телефон доверия (Россия): 8-800-2000-122**

---

## 📄 Лицензия

Этот проект лицензирован под MIT License.

---

<div align="center">

**Made with ❤️ using Vue 3, .NET 10 and MiMo**

</div>
