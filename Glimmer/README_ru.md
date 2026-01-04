# Glimmer

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![GLM-4V](https://img.shields.io/badge/GLM--4V-Zhipu_AI-2B5697?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Агент автоматизации для десктопа и мобильных устройств**

*На основе [Open-AutoGLM](https://github.com/THUDM/OpenAutoGLM) от Zhipu, поддержка автоматизации на desktop/Android/iOS/HarmonyOS*

[English](./README.md) | [中文](./README_zh.md) | Русский | [한국어](./README_ko.md) | [日本語](./README_ja.md)

</div>

---

## ✨ Возможности

- 🖥️ **Автоматизация десктопа** - Распознавание скриншотов, клики мышью, ввод с клавиатуры
- 📱 **Поддержка мобильных** - Android (ADB), iOS (XCTest), HarmonyOS (HDC)
- 🤖 **AI-управление** - Понимание экрана на основе GLM-4V / GPT-4o
- 🎯 **Целеориентированность** - Описание задач на естественном языке, авто-планирование шагов
- 📸 **Скриншоты в реальном времени** - Автозахват состояния экрана после каждого действия
- 🔄 **Пошаговый контроль** - Поддержка пошагового выполнения и непрерывного режима
- 🌐 **Web UI** - Визуальная панель управления на Vue 3

---

## 🛠️ Технологии

| Уровень | Технология | Версия | Назначение |
|---------|------------|--------|------------|
| Frontend UI | Vue + TypeScript + Vite | 3.5+ | Визуальная панель управления |
| Backend API | Python + HTTP Server | 3.10+ | Сервис агента |
| Десктоп | PyAutoGUI + Pillow | - | Скриншоты и симуляция ввода |
| Android | ADB | - | Управление устройством |
| iOS | XCTest | - | Управление устройством |
| HarmonyOS | HDC | - | Управление устройством |
| AI Модель | Zhipu GLM-4V | - | Визуальное понимание |

---

## 🏗️ Структура проекта

```
Glimmer/
├── Glimmer-UI/                  # Vue 3 Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel.vue       # Панель чата
│   │   │   ├── InputBar.vue        # Поле ввода
│   │   │   ├── ScreenshotViewer.vue # Просмотр скриншотов
│   │   │   └── StatusIndicator.vue # Индикатор статуса
│   │   ├── App.vue
│   │   └── main.ts
│   └── package.json
│
├── Glimmer-Web/                 # Python Backend API
│   ├── core/
│   │   ├── actions/            # Обработчики действий
│   │   ├── config/             # Конфигурация и промпты
│   │   ├── desktop/            # Модуль десктопных операций
│   │   ├── model/              # Клиент модели
│   │   └── agent.py            # Ядро агента
│   ├── server.py               # HTTP API сервис
│   └── requirements.txt
│
└── Open-AutoGLM/                # Библиотека автоматизации
    ├── glimmer/                 # Десктоп агент
    ├── phone_agent/             # Мобильный агент
    │   ├── adb/                 # Управление Android
    │   ├── xctest/              # Управление iOS
    │   └── hdc/                 # Управление HarmonyOS
    ├── glimmer_ui/              # Оригинальный UI
    └── examples/                # Примеры использования
```

---

## 🚀 Быстрый старт

### 1. Требования

- Node.js 18+
- Python 3.10+
- Zhipu AI GLM-4V API Key

### 2. Запуск Backend сервиса

```bash
cd Glimmer-Web
pip install -r requirements.txt
python server.py --host localhost --port 5000
```

### 3. Запуск Frontend UI

```bash
cd Glimmer-UI
npm install
npm run dev
```

Или используйте скрипты быстрого запуска:

**Windows:**
```bash
cd Glimmer-UI
.\start.bat
```

**Linux/macOS:**
```bash
cd Glimmer-UI
chmod +x start.sh && ./start.sh
```

### 4. URL-адреса

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

---

## 📡 API Эндпоинты

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/api/health` | Проверка статуса сервиса |
| GET | `/api/screenshot` | Получение текущего скриншота |
| POST | `/api/execute` | Выполнение шага агента |
| POST | `/api/reset` | Сброс состояния агента |
| POST | `/api/config` | Обновление конфигурации |

### Пример запроса выполнения

```json
{
  "goal": "Открыть Блокнот и написать Hello World",
  "model_url": "http://localhost:8000/v1",
  "model_name": "glm-4v"
}
```

### Пример ответа выполнения

```json
{
  "ui_thought": "Я вижу рабочий стол, нужно сначала открыть меню Пуск",
  "ui_focus_box": [100, 200, 150, 250],
  "status": "WORKING",
  "operation": {
    "action": "click",
    "params": {"x": 125, "y": 225}
  },
  "screenshot": "base64...",
  "confidence": 0.95
}
```

---

## ⚙️ Конфигурация

### Конфигурация модели

Через `/api/config` эндпоинт или при запуске:

```json
{
  "model_url": "https://open.bigmodel.cn/api/paas/v4",
  "model_name": "glm-4v",
  "api_key": "your-zhipu-api-key",
  "lang": "ru"
}
```

### Поддерживаемые модели

| Модель | Провайдер | Описание |
|--------|-----------|----------|
| GLM-4V | Zhipu AI | Рекомендуется, отличное понимание китайского |
| GLM-4V-Plus | Zhipu AI | Улучшенная версия, лучше для сложных сценариев |

---

## 📱 Использование на мобильных

### Android (ADB)

```bash
# Убедитесь что устройство подключено через adb
adb devices

# Используйте phone_agent
cd Open-AutoGLM
python main.py --device android
```

### iOS (XCTest)

См. [Руководство по настройке iOS](./Open-AutoGLM/docs/ios_setup/ios_setup.md)

### HarmonyOS (HDC)

```bash
# Убедитесь что устройство подключено через hdc
hdc list targets

python main.py --device harmonyos
```

---

## 🎬 Пример использования

```python
from glimmer import GlimmerAgent, AgentConfig
from glimmer.model.client import ModelConfig

# Настройка модели
model_config = ModelConfig(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model_name="glm-4v",
    api_key="your-zhipu-api-key"
)

# Создание агента
agent = GlimmerAgent(model_config, AgentConfig())

# Выполнение задачи
while True:
    result = agent.step("Открыть браузер и найти погоду")
    print(f"Мысль: {result.thought}")
    print(f"Действие: {result.action_type}")
    if result.finished:
        break
```

---

## 📄 Лицензия

Этот проект лицензирован под MIT License.

---

<div align="center">

**Made with ❤️ using Vue 3, Python and Vision AI**

</div>
