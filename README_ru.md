# HelloQoder

<div align="center">

![Projects](https://img.shields.io/badge/Projects-7-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-9.0%20|%2010.0-512BD4?style=flat-square&logo=dotnet)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Коллекция проектов от Qoder**

*Практика AI-управляемого агентного программирования*

[English](./README.md) | [中文](./README_zh.md) | Русский | [한국어](./README_ko.md) | [日本語](./README_ja.md)

</div>

---

## 📂 Список проектов

| Проект | Описание | Технологии | Статус |
|--------|----------|------------|--------|
| [ALAgent](./ALAgent/) | Автономный агент программирования для VS Code | .NET 10, TypeScript, Python, LightRAG | ✅ Active |
| [Glimmer](./Glimmer/) | Агент автоматизации для десктопа и мобильных | Vue 3, Python, Zhipu GLM-4V | ✅ Active |
| [CartService](./CartService/) | Микросервис корзины покупок для e-commerce | FastAPI, PostgreSQL, SQLAlchemy | ✅ Active |
| [NovelTTSApp](./NovelTTSApp/) | AI-приложение для преобразования романов в аудиокниги | .NET 10, Zhipu GLM-TTS, NAudio | ✅ Active |
| [EpubToSplitTxt](./EpubToSplitTxt/) | Инструмент разделения Epub по главам | .NET 9, VersOne.Epub | ✅ Active |
| [MindMates](./MindMates/) | AI-платформа для психологического здоровья | Vue 3, .NET 10, FastAPI, MiMo | ✅ Active |
| [BatchClip](./BatchClip/) | Инструмент автоматического пакетного редактирования видео | FastAPI, Streamlit, FFmpeg | ✅ Active |

---

## 🏗️ Структура директорий

```
HelloQoder/
├── ALAgent/                 # 🤖 Автономный агент программирования
│   ├── frontend-extension/  # Расширение VS Code
│   ├── backend-agent/       # .NET движок рассуждений
│   ├── backend-rag/         # Python RAG сервис
│   └── README.md            # Документация
│
├── Glimmer/                 # 🖥️ Автоматизация десктопа с AI
│   ├── Glimmer-UI/          # Vue 3 Frontend
│   ├── Glimmer-Web/         # Python Backend
│   ├── Open-AutoGLM/        # Библиотека автоматизации
│   └── README.md            # Документация
│
├── CartService/             # 🛒 Микросервис корзины
│   ├── app/                 # Код приложения
│   ├── alembic/             # Миграции БД
│   └── README.md            # Документация
│
├── NovelTTSApp/             # 🎙️ Приложение преобразования романа в речь
│   ├── src/
│   │   ├── Core/            # Ядро - Доменные сущности и интерфейсы
│   │   ├── Infrastructure/  # Инфраструктура - Реализации
│   │   └── App/             # Приложение - Главная программа
│   └── README.md            # Документация
│
├── EpubToSplitTxt/          # 📖 Инструмент разделения Epub
│   ├── EpubConverter.cs     # Парсер Epub
│   ├── TextSplitter.cs      # Разделитель глав
│   └── README.md            # Документация
│
├── MindMates/               # 🧠 AI-платформа психологического здоровья
│   ├── frontend/            # Vue 3 Frontend
│   ├── backend-business/    # .NET 10 бизнес-бэкенд
│   ├── backend-ai/          # Python AI бэкенд
│   └── README.md            # Документация
│
├── BatchClip/               # 🎬 Инструмент пакетного редактирования видео
│   ├── backend/             # FastAPI Backend
│   ├── frontend/            # Streamlit Frontend
│   └── start.bat            # Скрипт запуска
│
└── README.md                # Этот файл
```

---

## ✨ Быстрая навигация

### 🤖 ALAgent

Автономный агент программирования для VS Code, построенный на архитектуре Microsoft Agent Framework + LangChain + LightRAG.

- **Технологии**: TypeScript 5.0+ / .NET 10 / Python 3.11+ / LangChain / LightRAG
- **Функции**: Интеллектуальный чат, Поиск кода, Файловые операции, Анализ кода, Улучшенный поиск с графом знаний
- **Архитектура**: Расширение VS Code + .NET Agent + Python RAG сервис
- **Документация**: [Подробнее](./ALAgent/README.md)

---

### 🖥️ Glimmer

Агент автоматизации для десктопа и мобильных устройств на базе Zhipu Open-AutoGLM с кроссплатформенной поддержкой.

- **Технологии**: Vue 3 / Python 3.10+ / PyAutoGUI / Zhipu GLM-4V
- **Функции**: Автоматизация десктопа, Поддержка мобильных (Android/iOS/HarmonyOS), AI визуальное понимание
- **Архитектура**: Vue Frontend + Python Agent сервис
- **Документация**: [Подробнее](./Glimmer/README.md)

---

### 🛒 CartService

Высокопроизводительный микросервис корзины покупок с поддержкой CRUD, управления товарами, слияния корзин.

- **Технологии**: Python 3.10+ / FastAPI / PostgreSQL / SQLAlchemy 2.0
- **Функции**: Управление корзиной, CRUD товаров, Слияние корзин
- **Документация**: [Подробнее](./CartService/README.md)

---

### 🎙️ NovelTTSApp

AI-приложение для преобразования текста романов в аудиокниги с использованием Zhipu GLM-TTS.

- **Технологии**: .NET 10 / C# 13 / Zhipu GLM-TTS / NAudio
- **Функции**: Чтение текста романа, Умная сегментация, AI синтез речи, Клонирование голоса
- **Архитектура**: Clean Architecture
- **Документация**: [Подробнее](./NovelTTSApp/README.md)

---

### 📖 EpubToSplitTxt

Система предобработки Epub, преобразование `.epub` в текст с интеллектуальным разделением по главам.

- **Технологии**: .NET 9 / VersOne.Epub / HtmlAgilityPack
- **Функции**: Парсинг Epub, Распознавание глав, Умное разделение, UTF-8 вывод
- **Документация**: [Подробнее](./EpubToSplitTxt/README.md)

---

### 🧠 MindMates

AI-платформа для психологического здоровья с круглосуточными интеллектуальными консультациями.

- **Технологии**: Vue 3 + TypeScript / .NET 10 / Python FastAPI / MiMo
- **Функции**: AI чат, Обнаружение кризисов, RAG улучшение, Мобильная поддержка
- **Архитектура**: Разделение Frontend-Backend + AI микросервис
- **Документация**: [Подробнее](./MindMates/README.md)

---

### 🎬 BatchClip

Инструмент автоматического пакетного редактирования видео, AI анализирует материалы и создает черновые видео.

- **Технологии**: Python / FastAPI / Streamlit / FFmpeg
- **Функции**: Загрузка видео, AI анализ материалов, Авто черновая сборка, Пакетная обработка
- **Архитектура**: Разделение Frontend-Backend
- **Документация**: [Подробнее](./BatchClip/README.md)

---

## 🔧 Обзор технологий

| Область | Технологии |
|---------|------------|
| **Бэкенд сервисы** | Python, FastAPI, .NET 10 |
| **Фронтенд** | Vue 3, TypeScript, Vite |
| **AI интеграция** | Zhipu GLM-TTS, Zhipu GLM-4V, Xiaomi MiMo, LangChain, LightRAG |
| **Базы данных** | PostgreSQL, Milvus |
| **Обработка видео** | FFmpeg |
| **Развертывание** | Docker Compose |

---

## 📋 Добавление новых проектов

1. Создайте новую папку проекта в корневой директории
2. Добавьте код проекта и отдельный `README.md`
3. Опционально: Добавьте `Agent.md` и `Agent&Chat.md`
4. Обновите список проектов в этом файле

---

<div align="center">

**Made with ❤️ by Qoder**

</div>
