# NovelTTS

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**将小说文本转换为有声书的 AI 应用程序**

*使用智谱 GLM-4-Voice 实现高质量文本转语音，支持从 Bilibili 提取参考音频进行声音克隆*

</div>

---

## ✨ 功能特性

- 📖 **小说文本读取** - 支持 `.txt`、`.md` 文件，支持从 URL 抓取内容
- 🎯 **智能文本分段** - 自动将长文本分割为适合 TTS 的片段
- 🎙️ **AI 语音合成** - 基于智谱 GLM-4-Voice 的高质量语音生成
- 🎭 **声音克隆** - 从 Bilibili 视频提取参考音频实现声音克隆
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
    -v, --voice <url>      用于声音克隆的 Bilibili 视频 URL (可选)
    -h, --help             显示帮助信息
```

### 使用示例

```bash
# 处理默认输入文件夹中的所有小说
NovelTTSApp

# 处理单个小说文件
NovelTTSApp -i ./mynovel.txt -o ./mynovel.mp3

# 使用 Bilibili 视频进行声音克隆
NovelTTSApp -i ./novel.txt -v https://www.bilibili.com/video/BV1xxxxxxxx
```

---

## ⚙️ 配置说明

### appsettings.json

```json
{
  "AI": {
    "Endpoint": "https://open.bigmodel.cn/api/paas/v4/",
    "ApiKey": "YOUR_API_KEY",
    "ModelId": "glm-4-voice"
  },
  "Bilibili": {
    "Cookie": ""
  },
  "Paths": {
    "InputFolder": "./data/novels",
    "OutputFolder": "./data/output",
    "ReferenceAudioFolder": "./data/reference_audio",
    "TempFolder": "./data/temp"
  }
}
```

### 配置项说明

| 配置项 | 说明 |
|--------|------|
| `AI:Endpoint` | 智谱 API 端点地址 |
| `AI:ApiKey` | 智谱 API 密钥 |
| `AI:ModelId` | 使用的模型 ID |
| `Bilibili:Cookie` | B站 Cookie（可选，用于获取高清音频） |
| `Paths:InputFolder` | 小说文件输入目录 |
| `Paths:OutputFolder` | 音频输出目录 |

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

## 📚 开发文档

- [开发过程记录](./docs/DEVELOPMENT.md) - 项目创建与开发的完整记录

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<div align="center">

**Made with ❤️ using .NET 10 and AI**

</div>
