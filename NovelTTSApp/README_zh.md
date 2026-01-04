# NovelTTS

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**将小说文本转换为有声书的 AI 应用程序**

*使用智谱 GLM-TTS 实现高质量语音合成，支持 Bilibili 音频声音克隆*

[English](./README.md) | 中文 | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **开发过程记录**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 功能特性

- 📖 **小说文本读取** - 支持 `.txt`、`.md` 文件，支持从 URL 抓取内容
- 🎯 **智能文本分段** - 自动将长文本分割为适合 TTS 的片段
- 🎙️ **AI 语音合成** - 基于智谱 GLM-TTS 的高质量语音生成
- 🎭 **声音克隆** - 从 Bilibili 视频提取参考音频，通过 GLM-TTS-Clone 实现音色克隆
- 🎵 **音频处理** - 使用 NAudio 进行音频合并、格式转换
- 🔄 **智能重试** - 使用 Polly 处理 API 调用失败的重试机制
- 📊 **进度追踪** - 实时显示处理进度

---

## 🏗️ 架构设计

项目采用 **Clean Architecture（清洁架构）** 设计模式：

```
NovelTTSApp/
├── src/
│   ├── Core/                    # 核心层 - 领域实体与接口
│   │   ├── Entities/            # 领域实体
│   │   │   ├── Novel.cs         # 小说实体
│   │   │   ├── AudioSegment.cs  # 音频片段实体
│   │   │   └── VoiceReference.cs# 声音参考实体
│   │   └── Interfaces/          # 核心接口
│   │       ├── INovelReader.cs
│   │       ├── ITextSegmenter.cs
│   │       ├── ITtsService.cs
│   │       ├── IAudioProcessor.cs
│   │       ├── IBilibiliDownloader.cs
│   │       └── INovelProcessor.cs
│   │
│   ├── Infrastructure/          # 基础设施层 - 具体实现
│   │   ├── Configuration/       # 配置类
│   │   ├── Services/            # 服务实现
│   │   │   ├── NovelReader.cs
│   │   │   ├── TextSegmenter.cs
│   │   │   ├── ZhipuTtsService.cs
│   │   │   ├── AudioProcessor.cs
│   │   │   └── BilibiliDownloader.cs
│   │   └── DependencyInjection.cs
│   │
│   └── App/                     # 应用层 - 主程序
│       ├── Services/
│       │   └── NovelProcessor.cs
│       ├── Program.cs
│       └── appsettings.json
│
└── NovelTTSApp.sln
```

---

## 🚀 快速开始

### 环境要求

- [.NET 10.0 SDK](https://dotnet.microsoft.com/download) 或更高版本
- 智谱 AI API Key ([获取地址](https://open.bigmodel.cn/))

### 安装与配置

1. **克隆项目**
```bash
git clone https://github.com/your-repo/NovelTTSApp.git
cd NovelTTSApp
```

2. **配置 API Key**

编辑 `src/App/appsettings.json`：
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

3. **构建项目**
```bash
dotnet build -c Release
```

4. **运行程序**
```bash
dotnet run --project src/App
```

---

## 📖 使用方法

### 命令行参数

```bash
NovelTTSApp [options]

选项:
    -i, --input <path>     输入小说文件路径 (.txt 或 .md)
    -o, --output <path>    输出音频文件路径 (.mp3)
    -c, --chapter <name>   章节过滤关键词
    -v, --voice <url>      用于声音克隆的 Bilibili 视频 URL (可选)
    -h, --help             显示帮助信息
```

### 使用示例

```bash
# 处理默认输入文件夹中的所有小说
dotnet run --project src/App

# 处理特定章节
dotnet run --project src/App -- -c "第一章"

# 使用 Bilibili 视频进行声音克隆
dotnet run --project src/App -- -c "第一章" -v https://www.bilibili.com/video/BV1xxxxxxxx

# 处理单个小说文件
dotnet run --project src/App -- -i ./mynovel.txt -o ./mynovel.mp3
```

---

## 🎭 声音克隆

声音克隆功能通过智谱 GLM-TTS-Clone API 实现，完整流程：

```
1. 从 Bilibili 视频下载并提取参考音频（10秒片段）
2. 上传音频至智谱 API 获取 file_id（purpose: voice-clone-input）
3. 调用 voice/clone 创建音色 → 获得 voice_id
4. 使用 voice_id 调用 GLM-TTS 生成克隆语音
```

> 📚 参考文档：[GLM-TTS-Clone](https://docs.bigmodel.cn/cn/guide/models/sound-and-video/glm-tts-clone)

---

## 📁 数据目录结构

```
data/
├── novels/              # 小说文本源文件
│   └── 蛊真人/
│       └── 01.第一章：前言/
│           ├── 001.前言.txt
│           └── 002.内容简介....txt
├── output/              # 生成的有声书文件
├── reference_audio/     # B站提取的参考音频素材
└── temp/                # 临时音频片段文件
```

---

## 🔧 核心依赖

| 库 | 版本 | 用途 |
|----|------|------|
| Microsoft.Extensions.AI | 最新 | .NET AI 统一抽象层 |
| NAudio | 2.2.1 | 音频处理（格式转换、合并） |
| HtmlAgilityPack | 1.11.59 | HTML 解析（网页小说抓取） |
| Serilog | 4.2.0 | 结构化日志 |
| Polly | 8.0.0 | 弹性处理（重试机制） |

---

## 📊 业务流程

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   素材获取      │────▶│   文本处理      │────▶│   AI 生成       │
│                 │     │                 │     │                 │
│ • 读取小说文件  │     │ • 文本清洗      │     │ • 调用智谱 API  │
│ • B站音频提取   │     │ • 智能分段      │     │ • 流式处理      │
│ • 声音克隆准备  │     │ • 音色克隆      │     │ • 语音生成      │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   后期合成      │
                                               │                 │
                                               │ • 音频片段合并  │
                                               │ • 格式转换导出  │
                                               └─────────────────┘
```

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<div align="center">

**Made with ❤️ using .NET 10 and Zhipu AI**

</div>
