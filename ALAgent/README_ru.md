# AL Agent

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Автономный агент программирования для VS Code**

*Продвинутый AI-ассистент для программирования на основе мультимодальной RAG технологии, вдохновлённый [Cline](https://github.com/cline/cline)*

[English](./README.md) | [中文](./README_zh.md) | Русский | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Журнал разработки**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Возможности

- 🤖 **Интеллектуальный Code Agent** - Автономное программирование с помощью естественного языка
- 📚 **Мультимодальный RAG** - Улучшенный поиск с семантическим и графовым извлечением
- 🔧 **Вызов инструментов** - Файловые операции, анализ кода, системные команды
- 🌐 **Многоисточниковая загрузка** - Индексация веб-страниц, GitHub репозиториев и PDF
- 💬 **Контекстно-зависимый чат** - Поддержка контекста разговора для точных ответов

---

## 🏗️ Архитектура

```
AL Agent
├── frontend-extension/    # Расширение VS Code (TypeScript + React + Vite)
├── backend-agent/         # Движок рассуждений (.NET 10 + Microsoft Agent Framework)
└── backend-rag/          # RAG сервис (Python 3.13 + LangChain + LightRAG)
```

---

## 🛠️ Технологии

| Уровень | Технология | Версия | Назначение |
|---------|------------|--------|------------|
| Фронтенд | TypeScript + React + Vite | 5.0+ | Расширение VS Code |
| Agent Бэкенд | .NET + Microsoft Agent Framework | 10.0 | Движок рассуждений |
| RAG Бэкенд | Python + FastAPI + LangChain | 3.13 | Семантический поиск |
| Векторная БД | Milvus | 2.4+ | Хранение эмбеддингов |
| AI Модель | OpenAI / DashScope | - | LLM и Embeddings |

---

## 🚀 Быстрый старт

### Требования

- Node.js 18+
- .NET 10 SDK
- Python 3.11+ с менеджером пакетов uv
- Ключ API OpenAI или DashScope
- Векторная база данных Milvus (опционально, для продакшена)

### 1. Фронтенд расширение

```bash
cd frontend-extension
npm install
npm run watch  # Горячая перезагрузка для разработки
```

Отладка: Нажмите `F5` в VS Code для запуска расширения в режиме отладки.

### 2. Agent Бэкенд (.NET)

```bash
cd backend-agent
# Установите API ключ в appsettings.json или переменных окружения
dotnet run --urls=http://localhost:5000
```

### 3. RAG Бэкенд (Python)

```bash
cd backend-rag
uv venv                    # Создание виртуального окружения
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .        # Установка в режиме разработки

# Настройка окружения (скопируйте и отредактируйте)
cp .env.example .env
# Отредактируйте .env с вашими API ключами (DASHSCOPE_API_KEY или OPENAI_API_KEY)

# Запуск сервиса
fastapi dev app/main.py --port 8000
```

---

## 🌐 Конфигурация портов

| Сервис | Порт | Описание |
|--------|------|----------|
| .NET Agent API | 5000 | Получает промпты, возвращает вызовы инструментов |
| Python RAG API | 8000 | Получает запросы, возвращает фрагменты кода |
| VS Code Extension | Внутренний | Коммуникация Webview |

---

## ⚙️ Конфигурация

### Настройки VS Code

```json
{
  "alagent.agentApiUrl": "http://localhost:5000",
  "alagent.ragApiUrl": "http://localhost:8000",
  "alagent.openaiApiKey": ""  // Будет безопасно храниться в VS Code secrets
}
```

### Переменные окружения

**Agent Бэкенд (.NET):**
- `Agent__OpenAIApiKey`: Ключ API OpenAI (или используйте appsettings.json)
- `Agent__ModelId`: Используемая модель (по умолчанию: gpt-4o)
- `Agent__RagApiUrl`: URL RAG сервиса (по умолчанию: http://localhost:8000)

**RAG Бэкенд (Python):**
- `DASHSCOPE_API_KEY`: Ключ API DashScope для Qwen embeddings (рекомендуется)
- `OPENAI_API_KEY`: Ключ API OpenAI как запасной вариант
- `MILVUS_HOST/MILVUS_PORT`: Подключение к векторной БД (по умолчанию: localhost:19530)
- `TEXT_EMBEDDING_MODEL`: Модель эмбеддингов (по умолчанию: text-embedding-v4)
- `LIGHTRAG_QUERY_MODE`: Режим запроса (naive/local/global/hybrid/mix)

---

## 📡 API Эндпоинты

**RAG Сервис**: http://localhost:8000
- `/` - API документация
- `/health` - Проверка состояния
- `/api/query` - Семантический поиск
- `/api/index` - Индексация рабочего пространства
- `/api/load/web` - Загрузка веб-страниц
- `/api/load/github` - Загрузка GitHub репозиториев
- `/api/load/pdf` - Загрузка PDF
- `/api/lightrag/query` - Графовое извлечение

---

## 🧪 Тестирование

### Тестирование RAG извлечения

```bash
cd backend-rag
python scripts/evaluate_recall.py --workspace /path/to/test/workspace
```

Критерий успеха: Recall@5 > 0.8

---

## 📄 Лицензия

Этот проект лицензирован под MIT License.

---

<div align="center">

**Made with ❤️ using .NET 10, Python, and Vision AI**

</div>
