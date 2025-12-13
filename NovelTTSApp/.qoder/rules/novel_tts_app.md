---
trigger: always_on
alwaysApply: true
---
## Codebase (代码库基础)
告知 Agent 项目的基础技术栈和架构：

- **语言**: C# (目标框架 .NET 10 Preview)
- **项目类型**: 控制台应用 (Console Application)，兼容 Worker Service 模式。
- **架构模式**: 清洁架构 (Clean Architecture)
    - `Core`: 定义领域实体（如 `Novel`(小说), `AudioSegment`(音频片段)）和核心接口。
    - `Infrastructure`: 具体实现层。包含 Bilibili 下载器、MEAI 客户端实现、文件 I/O 操作。
    - `App`: 主程序逻辑与流程编排 (`NovelProcessor`)。
- **编码风格**: 现代 C# 风格 (Global usings, 文件范围命名空间, 主构造函数)。

## Dependencies (核心依赖)
仅列出关键库及其用途，帮助 Agent 正确调用：

- **`Microsoft.Extensions.AI`** (MEAI): .NET 统一 AI 抽象库。用于标准化调用智谱 AI 的 API（通过自定义 `IChatClient` 或 `IEmbeddingGenerator` 实现，或者适配 OpenAI 协议）。
- **`Microsoft.SemanticKernel`** (可选): 如果需要更复杂的 Agent 编排（如自动规划任务），可引入 SK 框架。
- **`Bililive.Bilibili`** (或类似库): 用于解析和提取 Bilibili 视频流（作为声音克隆的参考音频源）。
- **`NAudio:2.2.1`** 或 **`FFmpeg.AutoGen`**: 音频处理库。用于格式转换 (WAV/MP3) 和合并生成的音频片段。
- **`HtmlAgilityPack:1.11.59`**: 如果需要从网页抓取小说文本时使用。
- **`Microsoft.Extensions.Configuration:10.0.0`**: 配置管理（读取 appsettings）。
- **`Serilog:4.0.0`**: 结构化日志记录。
- **`Polly:8.0.0`**: 弹性处理库，用于 API 调用失败时的重试机制。

## Config (配置管理)
告诉 Agent 配置文件的位置及关键变量命名：

- **配置源**: `appsettings.json` 和 环境变量。
- **关键配置项**:
    - `AI:Endpoint`: "https://open.bigmodel.cn/api/paas/v4/" (智谱 API 地址)
    - `AI:ApiKey`: "YOUR_API_KEY"
    - `AI:ModelId`: "glm-4-voice"
    - `Bilibili:Cookie`: (可选) 用于获取高清音频流。
    - `Paths:InputFolder`: 小说文本源文件目录。
    - `Paths:OutputFolder`: 成品输出目录。

## Backing Services (外部服务与资源)
定义项目依赖的外部设施：

### Storage (存储)
- **本地文件系统**:
    - `/data/novels`: 待处理文本。
    - `/data/reference_audio`: B站提取的参考音频素材。
    - `/data/output`: 最终有声书文件。

### External APIs (外部接口)
- **智谱 GLM-4-Voice**:
    - 通过 `Microsoft.Extensions.AI` 抽象层进行调用。
    - 功能: 文本生成语音 (TTS)、声音克隆。
- **Bilibili**:
    - 角色: 音色参考源。

## Build and run (构建与运行)
- **构建**: `dotnet build -c Release`
- **运行**: `dotnet run --project App`
- **业务流程**:
    1. **素材获取**: 输入 Bilibili URL -> `Bililive` 提取音频 -> `NAudio` 截取参考片段。
    2. **文本处理**: 读取小说 -> 文本清洗 -> 智能分段。
    3. **AI 生成**: 使用 `Microsoft.Extensions.AI` 接口将文本 + 参考音频发送给智谱 GLM。
    4. **后期合成**: 将生成的音频片段序列合并导出。

## Logs (日志规范)
- **框架**: Serilog
- **约定**:
    - 使用结构化日志记录关键节点（如：开始下载、API 响应耗时、合成进度）。
    - 所有的异常必须记录 StackTrace。

## AI Coding Rules (AI 编码具体准则)
1.  **MEAI 标准化**: 在实现智谱 API 调用时，尽量实现或扩展 `Microsoft.Extensions.AI` 中的接口（如不直接支持，可封装为自定义 Service），保持代码对未来模型切换的兼容性。
2.  **异步 I/O**: 必须使用 `async/await` 处理所有网络请求和文件操作。
3.  **流式处理 (Streaming)**: 考虑到长文本合成的耗时，如果 API 支持，优先使用流式接收音频数据并实时写入文件，而非等待全部生成完毕。
4.  **防封控与重试**: 结合 `Polly` 处理 HTTP 429 (Too Many Requests) 错误。