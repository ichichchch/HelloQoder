# NovelTTS

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**AI-приложение для преобразования текста романов в аудиокниги**

*Высококачественный синтез речи с использованием Zhipu GLM-TTS и поддержкой клонирования голоса из Bilibili*

[English](./README.md) | [中文](./README_zh.md) | Русский | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Журнал разработки**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Возможности

- 📖 **Чтение текста романов** - Поддержка `.txt`, `.md` файлов и извлечение контента из URL
- 🎯 **Интеллектуальная сегментация текста** - Автоматическое разделение длинного текста на сегменты для TTS
- 🎙️ **AI синтез речи** - Высококачественная генерация голоса на основе Zhipu GLM-TTS
- 🎭 **Клонирование голоса** - Извлечение референсного аудио из видео Bilibili для клонирования через GLM-TTS-Clone
- 🎵 **Обработка аудио** - Объединение аудио и конвертация форматов с помощью NAudio
- 🔄 **Умные повторы** - Механизм повторных попыток при сбоях API с помощью Polly
- 📊 **Отслеживание прогресса** - Отображение прогресса обработки в реальном времени

---

## 🏗️ Архитектура

Проект использует паттерн **Clean Architecture**:

```
NovelTTSApp/
├── src/
│   ├── Core/                    # Ядро - Доменные сущности и интерфейсы
│   │   ├── Entities/            # Доменные сущности
│   │   │   ├── Novel.cs         # Сущность романа
│   │   │   ├── AudioSegment.cs  # Сущность аудиосегмента
│   │   │   └── VoiceReference.cs# Сущность голосовой ссылки
│   │   └── Interfaces/          # Основные интерфейсы
│   │       ├── INovelReader.cs
│   │       ├── ITextSegmenter.cs
│   │       ├── ITtsService.cs
│   │       ├── IAudioProcessor.cs
│   │       ├── IBilibiliDownloader.cs
│   │       └── INovelProcessor.cs
│   │
│   ├── Infrastructure/          # Инфраструктура - Реализации
│   │   ├── Configuration/       # Классы конфигурации
│   │   ├── Services/            # Реализации сервисов
│   │   │   ├── NovelReader.cs
│   │   │   ├── TextSegmenter.cs
│   │   │   ├── ZhipuTtsService.cs
│   │   │   ├── AudioProcessor.cs
│   │   │   └── BilibiliDownloader.cs
│   │   └── DependencyInjection.cs
│   │
│   └── App/                     # Приложение - Главная программа
│       ├── Services/
│       │   └── NovelProcessor.cs
│       ├── Program.cs
│       └── appsettings.json
│
└── NovelTTSApp.sln
```

---

## 🚀 Быстрый старт

### Требования

- [.NET 10.0 SDK](https://dotnet.microsoft.com/download) или выше
- Zhipu AI API Key ([Получить здесь](https://open.bigmodel.cn/))

### Установка и настройка

1. **Клонирование проекта**
```bash
git clone https://github.com/your-repo/NovelTTSApp.git
cd NovelTTSApp
```

2. **Настройка API Key**

Отредактируйте `src/App/appsettings.json`:
```json
{
  "AI": {
    "Endpoint": "https://open.bigmodel.cn/api/paas/v4/",
    "ApiKey": "YOUR_API_KEY_HERE",
    "ModelId": "glm-4-voice"
  },
  "Paths": {
    "InputFolder": "./data/novels",
    "OutputFolder": "./data/output",
    "ReferenceAudioFolder": "./data/reference_audio",
    "TempFolder": "./data/temp"
  }
}
```

3. **Сборка проекта**
```bash
dotnet build -c Release
```

4. **Запуск программы**
```bash
dotnet run --project src/App
```

---

## 📖 Использование

### Аргументы командной строки

```bash
NovelTTSApp [options]

Опции:
    -i, --input <path>     Путь к входному файлу романа (.txt или .md)
    -o, --output <path>    Путь к выходному аудиофайлу (.mp3)
    -c, --chapter <name>   Ключевое слово фильтра глав
    -v, --voice <url>      URL видео Bilibili для клонирования голоса (опционально)
    -h, --help             Показать справку
```

### Примеры использования

```bash
# Обработать все романы в папке по умолчанию
dotnet run --project src/App

# Обработать конкретную главу
dotnet run --project src/App -- -c "Глава 1"

# Использовать видео Bilibili для клонирования голоса
dotnet run --project src/App -- -c "Глава 1" -v https://www.bilibili.com/video/BV1xxxxxxxx

# Обработать один файл романа
dotnet run --project src/App -- -i ./mynovel.txt -o ./mynovel.mp3
```

---

## 🎭 Клонирование голоса

Клонирование голоса реализовано через Zhipu GLM-TTS-Clone API, полный процесс:

```
1. Загрузка и извлечение референсного аудио из видео Bilibili (10-секундный клип)
2. Загрузка аудио в Zhipu API для получения file_id (purpose: voice-clone-input)
3. Вызов voice/clone для создания голоса → получение voice_id
4. Использование voice_id для вызова GLM-TTS и генерации клонированного голоса
```

> 📚 Справка: [GLM-TTS-Clone](https://docs.bigmodel.cn/cn/guide/models/sound-and-video/glm-tts-clone)

---

## 📁 Структура директорий данных

```
data/
├── novels/              # Исходные текстовые файлы романов
│   └── BookName/
│       └── 01.Chapter1/
│           ├── 001.Prologue.txt
│           └── 002.Introduction.txt
├── output/              # Сгенерированные аудиокниги
├── reference_audio/     # Референсное аудио из Bilibili
└── temp/                # Временные аудиосегменты
```

---

## 🔧 Основные зависимости

| Библиотека | Версия | Назначение |
|------------|--------|------------|
| Microsoft.Extensions.AI | Последняя | .NET AI унифицированный слой абстракции |
| NAudio | 2.2.1 | Обработка аудио (конвертация, объединение) |
| HtmlAgilityPack | 1.11.59 | Парсинг HTML (извлечение веб-романов) |
| Serilog | 4.2.0 | Структурированное логирование |
| Polly | 8.0.0 | Устойчивость (механизм повторов) |

---

## 📊 Бизнес-процесс

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Подготовка     │────▶│ Обработка текста│────▶│  AI генерация   │
│                 │     │                 │     │                 │
│ • Чтение романа │     │ • Очистка текста│     │ • Вызов Zhipu   │
│ • Аудио Bilibili│     │ • Сегментация   │     │ • Поточная обр. │
│ • Клон голоса   │     │ • Клон голоса   │     │ • Генерация     │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │ Постобработка   │
                                               │                 │
                                               │ • Объединение   │
                                               │ • Конвертация   │
                                               └─────────────────┘
```

---

## 📄 Лицензия

Этот проект лицензирован под MIT License - см. файл [LICENSE](LICENSE) для деталей.

---

<div align="center">

**Made with ❤️ using .NET 10 and Zhipu AI**

</div>
