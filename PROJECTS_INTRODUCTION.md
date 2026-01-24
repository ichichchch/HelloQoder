# HelloQoder 项目介绍

**六个由 Qoder（AI 编程助手）开发的项目集合**

涵盖 AI Agent、视频处理、电商微服务、心理健康平台、工具应用等多个领域

**技术栈**：Python 3.10+ · .NET 9/10 · Vue 3 · TypeScript · FastAPI · PostgreSQL

**开源地址**：
- GitHub: https://github.com/ichichchch/HelloQoder
- Gitee: https://gitee.com/ichistudio/HelloQoder

---

## 目录

- [项目总览](#项目总览)
- [Glimmer - 桌面/移动自动化](#1-glimmer---桌面移动自动化)
- [CartService - 购物车微服务](#2-cartservice---购物车微服务)
- [NovelTTSApp - 小说转有声书](#3-novelttsapp---小说转有声书)
- [EpubToSplitTxt - Epub 切分工具](#4-epubtosplittxt---epub-切分工具)
- [MindMates - 心理健康 AI 平台](#5-mindmates---心理健康-ai-平台)
- [BatchClip - 批量视频编辑](#6-batchclip---批量视频编辑)
- [如何获取与使用](#如何获取与使用)

---

## 关于 Qoder 开发方式

HelloQoder 中的所有项目均由 **Qoder**（AI 编程助手）通过对话式交互完成开发。Qoder 是一种 Agentic Coding 工具，能够理解自然语言需求，自动规划任务并生成代码。

### 开发流程

```
用户描述需求 → Qoder 理解意图 → 自动生成代码 → 用户反馈 → 迭代优化
```

### .qoder 配置目录

每个项目可通过 `.qoder` 文件夹配置开发规则：

```
.qoder/
├── rules/              # 规则文件
│   ├── project.md      # 项目级规则（技术栈、架构约束）
│   └── coding.md       # 编码规范（命名、注释、风格）
└── memory/             # 项目记忆（可选）
```

**规则文件示例**：

```markdown
## Codebase
- 语言: C# (.NET 10)
- 架构: Clean Architecture

## AI Coding Rules
- 必须使用 async/await
- 优先使用流式处理
- 结合 Polly 处理重试
```

规则文件让 Qoder 理解项目的技术约束，从而生成符合规范的代码。

> 💡 **提示**：您可以查看各项目中的 `.qoder` 文件夹，了解该项目的开发规则和技术约束。

### 典型开发对话

| 用户输入 | Qoder 产出 |
|----------|------------|
| "基于 rules 完成应用程序" | 完整项目结构 + 15+ 文件 |
| "Code Review" | 代码审查 + 自动修复 |
| "添加购物车合并功能" | 接口定义 + 业务实现 + 测试 |

---

## 项目总览

HelloQoder 包含 6 个功能完整的应用，涵盖全栈项目、微服务、命令行工具等多种形态。

| 项目 | 领域 | 核心功能 | 技术栈 |
|------|------|----------|--------|
| **Glimmer** | 桌面自动化 | AI 驱动的跨平台自动化 | Vue 3 + Python + GLM-4V |
| **CartService** | 电商微服务 | 高性能购物车服务 | FastAPI + PostgreSQL |
| **NovelTTSApp** | 语音合成 | 小说转有声书应用 | .NET 10 + GLM-TTS |
| **EpubToSplitTxt** | 文本处理 | Epub 电子书切分 | .NET 9 + VersOne.Epub |
| **MindMates** | 心理健康 | AI 心理咨询平台 | Vue 3 + .NET 10 + MiMo |
| **BatchClip** | 视频编辑 | 批量视频剪辑工具 | FastAPI + FFmpeg + Streamlit |

---

## 1. Glimmer - 桌面/移动自动化

**技术栈**：Vue 3.5 · Python 3.10+ · 智谱 GLM-4V

### 项目简介

Glimmer 是一个基于智谱 [Open-AutoGLM](https://github.com/THUDM/OpenAutoGLM) 的桌面和移动端 AI 自动化代理。通过视觉理解模型（GLM-4V），它可以"看懂"屏幕内容并自动执行操作。

### 核心功能

- 🖥️ **桌面自动化** - 截图识别、鼠标点击、键盘输入
- 📱 **移动端支持** - Android (ADB)、iOS (XCTest)、HarmonyOS (HDC)
- 🤖 **AI 视觉理解** - 基于 GLM-4V 的屏幕内容理解
- 🎯 **目标导向执行** - 自然语言描述任务，自动规划步骤
- 📸 **实时截图反馈** - 每步操作后自动截图验证
- 🔄 **步进控制** - 支持单步执行和连续运行模式

### 项目结构

```
Glimmer/
├── Glimmer-UI/          # Vue 3 可视化控制面板
│   ├── src/components/
│   │   ├── ChatPanel.vue        # 对话面板
│   │   ├── ScreenshotViewer.vue # 截图展示
│   │   └── StatusIndicator.vue  # 状态指示
│   └── package.json
│
├── Glimmer-Web/         # Python 后端服务
│   ├── core/
│   │   ├── actions/     # 动作处理器
│   │   ├── desktop/     # 桌面操作模块
│   │   └── agent.py     # Agent 核心
│   └── server.py
│
└── Open-AutoGLM/        # 开源自动化库
    ├── glimmer/         # 桌面 Agent
    └── phone_agent/     # 移动端 Agent
```

### 使用示例

```python
from glimmer import GlimmerAgent, AgentConfig
from glimmer.model.client import ModelConfig

# 配置模型
model_config = ModelConfig(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model_name="glm-4v",
    api_key="your-api-key"
)

# 创建 Agent 并执行任务
agent = GlimmerAgent(model_config, AgentConfig())
result = agent.step("打开浏览器搜索天气预报")
print(f"思考: {result.thought}")
print(f"动作: {result.action_type}")
```

---

## 2. CartService - 购物车微服务

**技术栈**：Python 3.10+ · FastAPI · PostgreSQL 15+

### 项目简介

CartService 是一个高性能电商购物车微服务，基于 FastAPI + SQLAlchemy 2.0 异步架构，支持完整的购物车生命周期管理。

### 核心功能

- 🛒 **购物车管理** - 创建、查询、清空购物车
- 📦 **商品操作** - 添加、修改数量、删除商品
- 🔄 **购物车合并** - 匿名购物车与用户购物车合并
- ⚡ **异步架构** - 基于 async/await 的高性能设计
- 📊 **价格快照** - 商品添加时记录单价

### 数据模型

**购物车表 (carts)**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| user_id | UUID | 用户 ID（可空） |
| status | VARCHAR | 状态 |
| created_at | DATETIME | 创建时间 |

**购物车商品表 (cart_items)**：

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID | 主键 |
| cart_id | UUID | 购物车 ID |
| product_id | VARCHAR | 商品 SKU |
| quantity | INTEGER | 数量 |
| unit_price | DECIMAL | 单价 |

### API 接口

```
GET    /api/v1/carts/{cart_id}           # 获取购物车详情
POST   /api/v1/carts                     # 创建购物车
POST   /api/v1/carts/{cart_id}/items     # 添加商品
PATCH  /api/v1/carts/{cart_id}/items/{item_id}  # 修改数量
DELETE /api/v1/carts/{cart_id}/items/{item_id}  # 删除商品
DELETE /api/v1/carts/{cart_id}           # 清空购物车
POST   /api/v1/carts/{cart_id}/merge     # 合并购物车
```

### 快速启动

```bash
cd CartService
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
# 访问 http://127.0.0.1:8000/docs 查看 Swagger 文档
```

---

## 3. NovelTTSApp - 小说转有声书

**技术栈**：.NET 10 · C# 13

### 项目简介

NovelTTSApp 是一个 AI 驱动的小说转有声书应用，使用智谱 GLM-TTS 进行高质量语音合成，支持从 Bilibili 视频提取参考音频进行声音克隆。

### 核心功能

- 📖 **小说文本读取** - 支持 `.txt`、`.md` 文件及 URL 内容提取
- 🎯 **智能文本分段** - 自动将长文本切分为 TTS 适合的片段
- 🎙️ **AI 语音合成** - 基于智谱 GLM-TTS 的高质量语音生成
- 🎭 **声音克隆** - 从 Bilibili 视频提取参考音频进行声音克隆
- 🎵 **音频处理** - 使用 NAudio 进行音频合并和格式转换
- 🔄 **智能重试** - 使用 Polly 实现 API 调用失败重试

### 项目架构 (Clean Architecture)

```
src/
├── Core/                      # 核心层 - 领域实体与接口
│   ├── Entities/
│   │   ├── Novel.cs           # 小说实体
│   │   ├── AudioSegment.cs    # 音频片段实体
│   │   └── VoiceReference.cs  # 声音参考实体
│   └── Interfaces/
│       ├── INovelReader.cs
│       ├── ITtsService.cs
│       └── IAudioProcessor.cs
│
├── Infrastructure/            # 基础设施层 - 接口实现
│   └── Services/
│       ├── ZhipuTtsService.cs      # 智谱 TTS 服务
│       ├── AudioProcessor.cs        # 音频处理
│       └── BilibiliDownloader.cs    # B站音频下载
│
└── App/                       # 应用层 - 主程序
    ├── Services/NovelProcessor.cs
    └── Program.cs
```

### 声音克隆流程

```
1. 下载 Bilibili 视频音频 (10 秒片段)
       ↓
2. 上传至智谱 API → 获取 file_id
       ↓
3. 调用 voice/clone → 创建 voice_id
       ↓
4. 使用 voice_id 调用 GLM-TTS → 生成克隆语音
```

### 使用示例

```bash
# 处理默认输入文件夹中的所有小说
dotnet run --project src/App

# 处理特定章节
dotnet run --project src/App -- -c "第一章"

# 使用 Bilibili 视频进行声音克隆
dotnet run --project src/App -- -c "第一章" -v https://www.bilibili.com/video/BV1xxxxxxxx
```

---

## 4. EpubToSplitTxt - Epub 切分工具

**技术栈**：.NET 9 · C# 13

### 项目简介

EpubToSplitTxt 是一个 Epub 电子书预处理系统，将 `.epub` 格式电子书转换为纯文本，并智能识别章节结构进行切分。

### 核心功能

- ✅ 自动解析 Epub 文件结构，提取纯文本
- ✅ 智能章节标题识别（支持中英文格式）
- ✅ 按章节切分为独立 TXT 文件，带序号保持阅读顺序
- ✅ 支持序章、楔子、后记等特殊章节
- ✅ UTF-8 无 BOM 编码输出
- ✅ 流式处理大文件，内存占用低

### 支持的章节格式

| 格式 | 示例 |
|------|------|
| 中文数字 | 第一章、第二十章、第一百章 |
| 阿拉伯数字 | 第1章、第001章 |
| 英文格式 | Chapter 1、Chapter 2 |
| 特殊章节 | 序章、楔子、引子、后记、尾声 |

### 处理流程

```
[Epub 文件]
    ↓
[EpubConverter] 解析 Epub 结构
    ↓
[HTML 清理] 去除标签，转换实体
    ↓
[全文] 合并为单个 TXT 文件
    ↓
[TextSplitter] 逐行扫描匹配章节
    ↓
[章节文件] 按序号输出为独立文件
```

### 输出目录结构

```
SplitOutput/
└── 小说名/
    ├── 000_序章.txt
    ├── 001_第一章_重生.txt
    ├── 002_第二章_修炼.txt
    └── ...
```

### 快速使用

```bash
# 1. 将 epub 文件放入 RawEpub 目录
# 2. 运行程序
dotnet run

# 3. 在 SplitOutput 目录查看输出
```

---

## 5. MindMates - 心理健康 AI 平台

**技术栈**：Vue 3.5 · .NET 10 · Python 3.13 · 小米 MiMo

### 项目简介

MindMates 是一个心理健康 AI 伴侣平台，提供 7x24 小时智能心理咨询服务。基于小米 MiMo 大语言模型，集成 RAG 检索增强和危机检测机制。

### 核心功能

- ✅ 基于 MiMo LLM 的智能心理咨询对话
- ✅ RAG 增强的专业心理健康知识回答
- ✅ 自动危机检测与求助资源推荐
- ✅ 多轮对话上下文记忆
- ✅ 会话历史记录与管理
- ✅ JWT 用户认证系统
- ✅ Capacitor 跨平台移动端支持 (iOS/Android)
- ✅ Docker Compose 一键部署

### 系统架构

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend  │────▶│  Backend-Business │────▶│   Backend-AI    │
│  Vue 3 SPA  │     │   .NET 10 API    │     │ FastAPI + MiMo  │
└─────────────┘     └──────────────────┘     └─────────────────┘
        │                   │                        │
        ▼                   ▼                        ▼
   用户交互            PostgreSQL               Milvus
   会话管理            用户认证               RAG 检索
   消息展示            数据持久化             危机检测
```

### 项目结构

```
MindMates/
├── frontend/                  # Vue 3 前端应用
│   ├── src/
│   │   ├── api/              # API 客户端
│   │   ├── views/            # 页面组件
│   │   ├── stores/           # Pinia 状态管理
│   │   └── router/           # 路由配置
│   └── capacitor.config.ts   # 移动端配置
│
├── backend-business/          # .NET 业务后端 (Clean Architecture)
│   ├── MindMates.Api/        # API 层
│   ├── MindMates.Application/ # 应用层
│   ├── MindMates.Domain/     # 领域层
│   └── MindMates.Infrastructure/ # 基础设施层
│
└── backend-ai/               # Python AI 后端
    ├── app/
    │   ├── memory/           # 对话记忆系统
    │   ├── services/         # 聊天服务
    │   ├── llm.py            # MiMo LLM 集成
    │   ├── rag.py            # RAG 检索服务
    │   └── crisis_detector.py # 危机检测
    └── main.py
```

### 危机检测机制

当用户消息包含敏感关键词时，系统会优先返回求助资源：

```python
CRISIS_KEYWORDS = ["自杀", "结束生命", "不想活了", "想死", "伤害自己"]

def detect_crisis(message: str) -> bool:
    return any(keyword in message for keyword in CRISIS_KEYWORDS)
```

### 快速启动

```bash
# Windows - 一键启动所有服务
.\start-all.bat

# 或分别启动
.\start-frontend.bat       # http://localhost:5173
.\start-backend-business.bat  # http://localhost:5000
.\start-backend-ai.bat     # http://localhost:8000

# Docker 部署
docker compose up -d
```

---

## 6. BatchClip - 批量视频编辑

**技术栈**：Python 3.10+ · FastAPI · Streamlit · FFmpeg

### 项目简介

BatchClip 是一个自动化批量视频编辑工具，基于 FastAPI + FFmpeg + Streamlit 架构，支持视频上传、预处理、粗剪等完整工作流。

### 核心功能

- 📤 **批量上传** - 支持 MP4/MOV/AVI/MKV/WebM 等主流格式
- 🎞️ **代理生成** - 自动生成低分辨率代理文件加速预览
- ✂️ **视频分割** - 按时长自动分割长视频
- 🎬 **片段提取** - 精确提取指定时间范围片段
- 📋 **粗剪合成** - 多片段合成为粗剪视频
- 🤖 **自动粗剪** - 智能保留片头片尾快速预览
- 📁 **资产管理** - 统一管理视频资产和元数据

### 项目结构

```
BatchClip/
├── backend/
│   ├── api/                    # API 路由
│   │   ├── upload.py           # 视频上传
│   │   ├── assets.py           # 资产管理
│   │   ├── processing.py       # 预处理
│   │   └── editor.py           # 编辑功能
│   ├── modules/                # 业务模块
│   │   ├── dam.py              # 数字资产管理
│   │   ├── preprocessor.py     # 视频预处理器
│   │   └── editor.py           # 视频编辑器
│   ├── config.py               # 配置管理
│   └── main.py                 # 应用入口
│
└── frontend/
    ├── app.py                  # Streamlit UI
    └── requirements.txt
```

### API 接口

| 模块 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 上传 | POST | `/api/upload/single` | 上传单个视频 |
| 资产 | GET | `/api/assets/` | 获取资产列表 |
| 资产 | DELETE | `/api/assets/{id}` | 删除资产 |
| 处理 | POST | `/api/processing/{id}/preprocess` | 完整预处理 |
| 处理 | POST | `/api/processing/{id}/proxy` | 生成代理文件 |
| 编辑 | POST | `/api/editor/{id}/clip` | 提取片段 |
| 编辑 | POST | `/api/editor/{id}/rough-cut` | 粗剪合成 |

### 使用流程

```
1. 上传视频
   └─> 📤 在上传页面上传 MP4/MOV 等视频文件

2. 预处理
   └─> ⚙️ 在处理页面生成代理/提取元数据

3. 编辑剪辑
   └─> ✂️ 在编辑页面提取片段或粗剪

4. 查看成果
   └─> 📁 在资产页面管理输出文件
```

### 快速启动

```bash
# Windows 一键启动
.\start.bat

# 或手动启动
cd backend && uvicorn main:app --reload --port 8000
cd frontend && streamlit run app.py --server.port 8501

# 访问
# 前端 UI: http://localhost:8501
# 后端 API: http://localhost:8000/docs
```

---

## 如何获取与使用

### 仓库地址

| 平台 | 地址 |
|------|------|
| **GitHub** | https://github.com/ichichchch/HelloQoder |
| **Gitee** | https://gitee.com/ichistudio/HelloQoder |

### 克隆项目

```bash
# GitHub
git clone https://github.com/ichichchch/HelloQoder.git

# Gitee (国内镜像)
git clone https://gitee.com/ichistudio/HelloQoder.git
```

### 环境要求

| 依赖 | 版本要求 |
|------|----------|
| Python | 3.10+ |
| .NET SDK | 9.0 / 10.0 |
| Node.js | 18+ |
| PostgreSQL | 15+ (部分项目需要) |
| FFmpeg | 最新版 (BatchClip 需要) |

### 项目独立运行

每个项目都可以独立运行，进入对应项目目录后参考其 `README.md` 文件获取详细启动说明。

---

## 技术栈总览

```
后端服务
├── Python 生态
│   ├── FastAPI (异步 Web 框架)
│   ├── LangChain (LLM 编排)
│   ├── SQLAlchemy 2.0 (异步 ORM)
│   └── Streamlit (快速 UI)
│
├── .NET 生态
│   ├── .NET 9 / 10
│   ├── Microsoft Agent Framework
│   ├── Entity Framework Core
│   └── NAudio (音频处理)

前端
├── Vue 3 + TypeScript + Vite
├── Element Plus / Tailwind CSS
└── VS Code Extension API

AI 模型
├── 智谱 GLM-4V / GLM-TTS
├── 小米 MiMo
├── OpenAI / DashScope 兼容
└── LightRAG (知识图谱)

数据存储
├── PostgreSQL (关系型)
├── Milvus (向量数据库)
└── 文件系统 (媒体资产)

部署
├── Docker Compose
├── Nginx 反向代理
└── Capacitor (移动端)
```

---

## 贡献与反馈

欢迎提交 Issue 和 Pull Request！

如有问题或建议，请通过以下方式联系：

- [GitHub Issues](https://github.com/ichichchch/HelloQoder/issues)
- [Gitee Issues](https://gitee.com/ichistudio/HelloQoder/issues)

---

**Made with ❤️ by Qoder**

*探索 AI 驱动开发的无限可能*

GitHub: https://github.com/ichichchch/HelloQoder

Gitee: https://gitee.com/ichistudio/HelloQoder
