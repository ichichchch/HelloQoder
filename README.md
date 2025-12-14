# HelloQoder

<div align="center">

![Projects](https://img.shields.io/badge/Projects-3-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-9.0%20|%2010.0-512BD4?style=flat-square&logo=dotnet)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Qoder 编写的项目集合**

*AI 驱动的 Agentic Coding 实践*

</div>

---

## 📂 项目列表

| 项目 | 描述 | 技术栈 | 状态 |
|------|------|--------|------|
| [CartService](./CartService/) | 电商购物车微服务 | FastAPI, PostgreSQL, SQLAlchemy | ✅ Active |
| [NovelTTSApp](./NovelTTSApp/) | 小说转有声书 AI 应用 | .NET 10, 智谱 GLM-TTS, NAudio | ✅ Active |
| [EpubToSplitTxt](./EpubToSplitTxt/) | Epub 电子书章节切分工具 | .NET 9, VersOne.Epub | ✅ Active |

---

## 🏗️ 目录结构

```
HelloQoder/
├── CartService/             # 🛒 购物车微服务
│   ├── app/                 # 应用代码
│   ├── alembic/             # 数据库迁移
│   └── README.md            # 项目文档
│
├── NovelTTSApp/             # 🎙️ 小说转语音应用
│   ├── src/
│   │   ├── Core/            # 核心层 - 领域实体与接口
│   │   ├── Infrastructure/  # 基础设施层 - 具体实现
│   │   └── App/             # 应用层 - 主程序
│   └── README.md            # 项目文档
│
├── EpubToSplitTxt/          # 📖 Epub 切分工具
│   ├── EpubConverter.cs     # Epub 解析器
│   ├── TextSplitter.cs      # 章节切分器
│   └── README.md            # 项目文档
│
└── README.md                # 本文件
```

---

## ✨ 快速导航

### 🛒 CartService

高性能电商购物车微服务，支持购物车 CRUD、商品管理、购物车合并等功能。

- **技术栈**: Python 3.10+ / FastAPI / PostgreSQL / SQLAlchemy 2.0
- **功能**: 购物车管理、商品增删改查、购物车合并
- **文档**: [查看详情](./CartService/README.md)

---

### 🎙️ NovelTTSApp

将小说文本转换为有声书的 AI 应用程序，使用智谱 GLM-TTS 实现高质量语音合成。

- **技术栈**: .NET 10 / C# 13 / 智谱 GLM-TTS / NAudio
- **功能**: 小说文本读取、智能分段、AI 语音合成、声音克隆
- **架构**: Clean Architecture（清洁架构）
- **文档**: [查看详情](./NovelTTSApp/README.md)

---

### 📖 EpubToSplitTxt

Epub 电子书预处理系统，将 `.epub` 格式电子书转换为纯文本并按章节智能切分。

- **技术栈**: .NET 9 / VersOne.Epub / HtmlAgilityPack
- **功能**: Epub 解析、章节识别、智能切分、UTF-8 输出
- **文档**: [查看详情](./EpubToSplitTxt/README.md)

---

## 🔧 技术栈总览

| 领域 | 技术 |
|------|------|
| **后端服务** | Python, FastAPI, SQLAlchemy |
| **桌面应用** | .NET 9/10, C# 13 |
| **AI 集成** | 智谱 GLM-TTS, 声音克隆 |
| **数据库** | PostgreSQL |
| **音频处理** | NAudio |

---

## 📋 添加新项目

1. 在根目录下创建新项目文件夹
2. 添加项目代码和独立的 `README.md`
3. 可选：添加 `Agent.md` 和 `Agent&Chat.md`
4. 更新本文件的项目列表

---

<div align="center">

**Made with ❤️ by Qoder**

</div>
