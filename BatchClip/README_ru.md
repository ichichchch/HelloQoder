# BatchClip

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Инструмент автоматического пакетного редактирования видео**

*Архитектура на базе FastAPI + FFmpeg + Streamlit, поддержка загрузки видео, предобработки и черновой сборки*

[English](./README.md) | [中文](./README_zh.md) | Русский | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Журнал разработки**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Возможности

- 📤 **Пакетная загрузка** - Поддержка MP4/MOV/AVI/MKV/WebM и других основных форматов
- 🎞️ **Генерация прокси** - Автоматическое создание прокси-файлов низкого разрешения для быстрого просмотра
- ✂️ **Разделение видео** - Автоматическое разделение длинных видео по длительности
- 🎬 **Извлечение клипов** - Точное извлечение сегментов указанного временного диапазона
- 📋 **Черновая сборка** - Объединение нескольких клипов в черновое видео
- 🤖 **Автоматическая черновая сборка** - Интеллектуальное сохранение вступления/окончания для быстрого просмотра
- 📁 **Управление ресурсами** - Унифицированное управление видеоресурсами и метаданными
- 📊 **Журналы обработки** - Полная запись истории обработки

---

## 🛠️ Технологии

| Технология | Версия | Назначение |
|------------|--------|------------|
| Python | 3.10+ | Среда выполнения |
| FastAPI | 0.109+ | Высокопроизводительный асинхронный Backend API |
| Streamlit | 1.40+ | Интерфейс Frontend |
| FFmpeg | - | Движок обработки видео |
| Pydantic | v2 | Валидация данных и конфигурация |
| aiofiles | 23.2+ | Асинхронные файловые операции |

---

## 🏗️ Структура проекта

```
BatchClip/
├── backend/
│   ├── api/                    # API маршруты
│   │   ├── upload.py           # API загрузки видео
│   │   ├── assets.py           # API управления ресурсами
│   │   ├── processing.py       # API предобработки
│   │   └── editor.py           # API редактирования
│   ├── modules/                # Бизнес-модули
│   │   ├── dam.py              # Управление цифровыми ресурсами
│   │   ├── upload_handler.py   # Обработчик загрузки
│   │   ├── preprocessor.py     # Препроцессор видео
│   │   └── editor.py           # Редактор видео
│   ├── config.py               # Управление конфигурацией
│   ├── main.py                 # Точка входа приложения
│   └── requirements.txt        # Зависимости Backend
├── frontend/
│   ├── app.py                  # Streamlit UI
│   └── requirements.txt        # Зависимости Frontend
├── start.bat                   # Скрипт запуска Windows
├── start.sh                    # Скрипт запуска Linux/Mac
└── .gitignore
```

---

## 🚀 Быстрый старт

### 1. Требования

- Python 3.10+
- FFmpeg (должен быть установлен и добавлен в PATH)

**Установка FFmpeg:**

```bash
# Windows (используя winget)
winget install FFmpeg

# Windows (используя choco)
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 2. Запуск одной командой

**Windows:**
```bash
.\start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

### 3. Ручной запуск

**Запуск Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Запуск Frontend:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### 4. URL-адреса

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📡 API Эндпоинты

### Модуль загрузки

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/upload/single` | Загрузка одного видео |
| GET | `/api/upload/list` | Получение списка загрузок |

### Модуль ресурсов

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/assets/` | Получение списка ресурсов |
| GET | `/api/assets/{asset_id}` | Получение деталей ресурса |
| GET | `/api/assets/{asset_id}/logs` | Получение журналов обработки |
| DELETE | `/api/assets/{asset_id}` | Удаление ресурса |

### Модуль обработки

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/processing/{asset_id}/preprocess` | Полная предобработка |
| POST | `/api/processing/{asset_id}/metadata` | Извлечение метаданных |
| POST | `/api/processing/{asset_id}/proxy` | Генерация прокси-файла |
| POST | `/api/processing/{asset_id}/split` | Разделение видео |

### Модуль редактора

| Метод | Путь | Описание |
|-------|------|----------|
| POST | `/api/editor/{asset_id}/clip` | Извлечение клипа |
| POST | `/api/editor/{asset_id}/rough-cut` | Черновая сборка |
| POST | `/api/editor/{asset_id}/auto-rough-cut` | Автоматическая черновая сборка |

---

## ⚙️ Конфигурация

### Переменные окружения (`backend/.env`)

```env
# Пути хранения
PROCESSING_TEMP_DIR=./temp
FINAL_OUTPUT_DIR=./output
UPLOAD_DIR=./uploads
ASSETS_DIR=./assets

# Тип хранилища (local/oss)
STORAGE_TYPE=local

# Путь к FFmpeg (если не в PATH)
FFMPEG_PATH=ffmpeg

# Конфигурация сервиса
HOST=0.0.0.0
PORT=8000

# Конфигурация обработки
MAX_UPLOAD_SIZE_MB=500
PROXY_RESOLUTION=720
DEFAULT_SEGMENT_DURATION=60

# Уровень логирования
LOG_LEVEL=INFO
```

---

## 🎬 Рабочий процесс

```
1. Загрузка видео
   └─> 📤 Загрузка MP4/MOV и других видеофайлов на странице Upload

2. Предобработка
   └─> ⚙️ Генерация прокси/извлечение метаданных на странице Processing

3. Редактирование
   └─> ✂️ Извлечение клипов или черновая сборка на странице Editor

4. Просмотр результатов
   └─> 📁 Управление выходными файлами на странице Assets
```

---

## 📂 Описание директорий

| Директория | Назначение |
|------------|------------|
| `uploads/` | Хранение оригинальных загруженных файлов |
| `assets/` | JSON файлы метаданных ресурсов |
| `temp/` | Временные файлы обработки |
| `output/` | Финальные выходные файлы |

---

## 📄 Лицензия

Этот проект лицензирован под MIT License.

---

<div align="center">

**Made with ❤️ using Python, FastAPI and FFmpeg**

</div>
