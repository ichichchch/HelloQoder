# HelloQoder

<div align="center">

![Projects](https://img.shields.io/badge/Projects-6-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-9.0%20|%2010.0-512BD4?style=flat-square&logo=dotnet)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Collection of Projects Written by Qoder**

*AI-Driven Agentic Coding Practice*

English | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

</div>

---

## 📂 Project List

| Project | Description | Tech Stack | Status |
|---------|-------------|------------|--------|
| [Glimmer](./Glimmer/) | Desktop & Mobile AI Automation Agent | Vue 3, Python, Zhipu GLM-4V | ✅ Active |
| [CartService](./CartService/) | E-commerce Shopping Cart Microservice | FastAPI, PostgreSQL, SQLAlchemy | ✅ Active |
| [NovelTTSApp](./NovelTTSApp/) | Novel to Audiobook AI Application | .NET 10, Zhipu GLM-TTS, NAudio | ✅ Active |
| [EpubToSplitTxt](./EpubToSplitTxt/) | Epub eBook Chapter Splitting Tool | .NET 9, VersOne.Epub | ✅ Active |
| [MindMates](./MindMates/) | Mental Health AI Companion Platform | Vue 3, .NET 10, FastAPI, MiMo | ✅ Active |
| [BatchClip](./BatchClip/) | Automated Batch Video Editing Tool | FastAPI, Streamlit, FFmpeg | ✅ Active |

---

## 🏗️ Directory Structure

```
HelloQoder/
├── Glimmer/                 # 🖥️ Desktop AI Automation
│   ├── Glimmer-UI/          # Vue 3 Frontend
│   ├── Glimmer-Web/         # Python Backend
│   ├── Open-AutoGLM/        # Open Source Automation Library
│   └── README.md            # Project Documentation
│
├── CartService/             # 🛒 Shopping Cart Microservice
│   ├── app/                 # Application Code
│   ├── alembic/             # Database Migrations
│   └── README.md            # Project Documentation
│
├── NovelTTSApp/             # 🎙️ Novel to Speech Application
│   ├── src/
│   │   ├── Core/            # Core Layer - Domain Entities & Interfaces
│   │   ├── Infrastructure/  # Infrastructure Layer - Implementations
│   │   └── App/             # Application Layer - Main Program
│   └── README.md            # Project Documentation
│
├── EpubToSplitTxt/          # 📖 Epub Splitting Tool
│   ├── EpubConverter.cs     # Epub Parser
│   ├── TextSplitter.cs      # Chapter Splitter
│   └── README.md            # Project Documentation
│
├── MindMates/               # 🧠 Mental Health AI Platform
│   ├── frontend/            # Vue 3 Frontend
│   ├── backend-business/    # .NET 10 Business Backend
│   ├── backend-ai/          # Python AI Backend
│   └── README.md            # Project Documentation
│
├── BatchClip/               # 🎬 Batch Video Editing Tool
│   ├── backend/             # FastAPI Backend
│   ├── frontend/            # Streamlit Frontend
│   └── start.bat            # Startup Script
│
└── README.md                # This File
```

---

## ✨ Quick Navigation

### 🖥️ Glimmer

Desktop and Mobile AI Automation Agent, based on Zhipu Open-AutoGLM, supporting cross-platform automation.

- **Tech Stack**: Vue 3 / Python 3.10+ / PyAutoGUI / Zhipu GLM-4V
- **Features**: Desktop Automation, Mobile Support (Android/iOS/HarmonyOS), AI Visual Understanding
- **Architecture**: Vue Frontend + Python Agent Service
- **Documentation**: [View Details](./Glimmer/README.md)

---

### 🛒 CartService

High-performance e-commerce shopping cart microservice, supporting cart CRUD, item management, cart merging, etc.

- **Tech Stack**: Python 3.10+ / FastAPI / PostgreSQL / SQLAlchemy 2.0
- **Features**: Cart Management, Item CRUD, Cart Merging
- **Documentation**: [View Details](./CartService/README.md)

---

### 🎙️ NovelTTSApp

AI application for converting novel text to audiobooks, using Zhipu GLM-TTS for high-quality speech synthesis.

- **Tech Stack**: .NET 10 / C# 13 / Zhipu GLM-TTS / NAudio
- **Features**: Novel Text Reading, Smart Segmentation, AI Speech Synthesis, Voice Cloning
- **Architecture**: Clean Architecture
- **Documentation**: [View Details](./NovelTTSApp/README.md)

---

### 📖 EpubToSplitTxt

Epub eBook preprocessing system, converting `.epub` format eBooks to plain text with intelligent chapter splitting.

- **Tech Stack**: .NET 9 / VersOne.Epub / HtmlAgilityPack
- **Features**: Epub Parsing, Chapter Recognition, Smart Splitting, UTF-8 Output
- **Documentation**: [View Details](./EpubToSplitTxt/README.md)

---

### 🧠 MindMates

Mental Health AI Companion Platform, providing 24/7 intelligent psychological counseling services.

- **Tech Stack**: Vue 3 + TypeScript / .NET 10 / Python FastAPI / MiMo
- **Features**: AI Chat, Crisis Detection, RAG Enhancement, Mobile Support
- **Architecture**: Frontend-Backend Separation + AI Microservice
- **Documentation**: [View Details](./MindMates/README.md)

---

### 🎬 BatchClip

Automated batch video editing tool, AI analyzes materials and automatically generates rough cut videos.

- **Tech Stack**: Python / FastAPI / Streamlit / FFmpeg
- **Features**: Video Upload, AI Material Analysis, Auto Rough Cut, Batch Processing
- **Architecture**: Frontend-Backend Separation
- **Documentation**: [View Details](./BatchClip/README.md)

---

## 🔧 Tech Stack Overview

| Domain | Technologies |
|--------|--------------|
| **Backend Services** | Python, FastAPI, .NET 10 |
| **Frontend** | Vue 3, TypeScript, Vite |
| **AI Integration** | Zhipu GLM-TTS, Zhipu GLM-4V, Xiaomi MiMo, LangChain, LightRAG |
| **Database** | PostgreSQL, Milvus |
| **Video Processing** | FFmpeg |
| **Deployment** | Docker Compose |

---

## 📋 Adding New Projects

1. Create a new project folder in the root directory
2. Add project code and standalone `README.md`
3. Optional: Add `Agent.md` and `Agent&Chat.md`
4. Update the project list in this file

---

<div align="center">

**Made with ❤️ by Qoder**

</div>
