# NovelTTS

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**AI Application for Converting Novel Text to Audiobooks**

*High-quality speech synthesis using Zhipu GLM-TTS with Bilibili audio voice cloning support*

English | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Development Log**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Features

- 📖 **Novel Text Reading** - Supports `.txt`, `.md` files, and URL content extraction
- 🎯 **Intelligent Text Segmentation** - Automatically split long text into TTS-suitable segments
- 🎙️ **AI Speech Synthesis** - High-quality voice generation based on Zhipu GLM-TTS
- 🎭 **Voice Cloning** - Extract reference audio from Bilibili videos for voice cloning via GLM-TTS-Clone
- 🎵 **Audio Processing** - Audio merging and format conversion using NAudio
- 🔄 **Smart Retry** - Retry mechanism for API call failures using Polly
- 📊 **Progress Tracking** - Real-time processing progress display

---

## 🏗️ Architecture

The project adopts **Clean Architecture** design pattern:

```
NovelTTSApp/
├── src/
│   ├── Core/                    # Core Layer - Domain Entities & Interfaces
│   │   ├── Entities/            # Domain Entities
│   │   │   ├── Novel.cs         # Novel Entity
│   │   │   ├── AudioSegment.cs  # Audio Segment Entity
│   │   │   └── VoiceReference.cs# Voice Reference Entity
│   │   └── Interfaces/          # Core Interfaces
│   │       ├── INovelReader.cs
│   │       ├── ITextSegmenter.cs
│   │       ├── ITtsService.cs
│   │       ├── IAudioProcessor.cs
│   │       ├── IBilibiliDownloader.cs
│   │       └── INovelProcessor.cs
│   │
│   ├── Infrastructure/          # Infrastructure Layer - Implementations
│   │   ├── Configuration/       # Configuration Classes
│   │   ├── Services/            # Service Implementations
│   │   │   ├── NovelReader.cs
│   │   │   ├── TextSegmenter.cs
│   │   │   ├── ZhipuTtsService.cs
│   │   │   ├── AudioProcessor.cs
│   │   │   └── BilibiliDownloader.cs
│   │   └── DependencyInjection.cs
│   │
│   └── App/                     # Application Layer - Main Program
│       ├── Services/
│       │   └── NovelProcessor.cs
│       ├── Program.cs
│       └── appsettings.json
│
└── NovelTTSApp.sln
```

---

## 🚀 Quick Start

### Prerequisites

- [.NET 10.0 SDK](https://dotnet.microsoft.com/download) or higher
- Zhipu AI API Key ([Get here](https://open.bigmodel.cn/))

### Installation & Configuration

1. **Clone Project**
```bash
git clone https://github.com/your-repo/NovelTTSApp.git
cd NovelTTSApp
```

2. **Configure API Key**

Edit `src/App/appsettings.json`:
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

3. **Build Project**
```bash
dotnet build -c Release
```

4. **Run Program**
```bash
dotnet run --project src/App
```

---

## 📖 Usage

### Command Line Arguments

```bash
NovelTTSApp [options]

Options:
    -i, --input <path>     Input novel file path (.txt or .md)
    -o, --output <path>    Output audio file path (.mp3)
    -c, --chapter <name>   Chapter filter keyword
    -v, --voice <url>      Bilibili video URL for voice cloning (optional)
    -h, --help             Show help information
```

### Usage Examples

```bash
# Process all novels in default input folder
dotnet run --project src/App

# Process specific chapter
dotnet run --project src/App -- -c "Chapter 1"

# Use Bilibili video for voice cloning
dotnet run --project src/App -- -c "Chapter 1" -v https://www.bilibili.com/video/BV1xxxxxxxx

# Process single novel file
dotnet run --project src/App -- -i ./mynovel.txt -o ./mynovel.mp3
```

---

## 🎭 Voice Cloning

Voice cloning is implemented via Zhipu GLM-TTS-Clone API, complete workflow:

```
1. Download and extract reference audio from Bilibili video (10-second clip)
2. Upload audio to Zhipu API to get file_id (purpose: voice-clone-input)
3. Call voice/clone to create voice → obtain voice_id
4. Use voice_id to call GLM-TTS to generate cloned voice
```

> 📚 Reference: [GLM-TTS-Clone](https://docs.bigmodel.cn/cn/guide/models/sound-and-video/glm-tts-clone)

---

## 📁 Data Directory Structure

```
data/
├── novels/              # Novel text source files
│   └── BookName/
│       └── 01.Chapter1/
│           ├── 001.Prologue.txt
│           └── 002.Introduction.txt
├── output/              # Generated audiobook files
├── reference_audio/     # Reference audio from Bilibili
└── temp/                # Temporary audio segment files
```

---

## 🔧 Core Dependencies

| Library | Version | Purpose |
|---------|---------|---------|
| Microsoft.Extensions.AI | Latest | .NET AI Unified Abstraction Layer |
| NAudio | 2.2.1 | Audio Processing (format conversion, merging) |
| HtmlAgilityPack | 1.11.59 | HTML Parsing (web novel extraction) |
| Serilog | 4.2.0 | Structured Logging |
| Polly | 8.0.0 | Resilience (retry mechanism) |

---

## 📊 Business Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Asset Prep    │────▶│  Text Process   │────▶│   AI Generate   │
│                 │     │                 │     │                 │
│ • Read novel    │     │ • Text cleaning │     │ • Call Zhipu API│
│ • B站 audio     │     │ • Smart segment │     │ • Stream process│
│ • Voice clone   │     │ • Voice clone   │     │ • Voice generate│
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   Post Process  │
                                               │                 │
                                               │ • Merge segments│
                                               │ • Format convert│
                                               └─────────────────┘
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Made with ❤️ using .NET 10 and Zhipu AI**

</div>
