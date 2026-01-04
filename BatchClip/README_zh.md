# BatchClip

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**自动化视频批量剪辑工具**

*基于 FastAPI + FFmpeg + Streamlit 架构，支持视频上传、预处理、粗剪全流程*

[English](./README.md) | 中文 | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **开发过程记录**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 功能特性

- 📤 **批量上传** - 支持 MP4/MOV/AVI/MKV/WebM 等主流格式
- 🎞️ **代理生成** - 自动生成低分辨率代理文件，加速预览
- ✂️ **视频分割** - 按时长自动切分长视频
- 🎬 **片段提取** - 精确提取指定时间段片段
- 📋 **粗剪合成** - 多片段拼接生成粗剪视频
- 🤖 **自动粗剪** - 智能保留片头片尾，快速生成预览
- 📁 **资产管理** - 统一管理视频素材及元数据
- 📊 **处理日志** - 完整记录处理过程

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 运行环境 |
| FastAPI | 0.109+ | 高性能异步后端 API |
| Streamlit | 1.40+ | 前端 UI 界面 |
| FFmpeg | - | 视频处理引擎 |
| Pydantic | v2 | 数据验证与配置管理 |
| aiofiles | 23.2+ | 异步文件操作 |

---

## 🏗️ 项目结构

```
BatchClip/
├── backend/
│   ├── api/                    # API 路由层
│   │   ├── upload.py           # 视频上传接口
│   │   ├── assets.py           # 资产管理接口
│   │   ├── processing.py       # 预处理接口
│   │   └── editor.py           # 剪辑接口
│   ├── modules/                # 业务模块
│   │   ├── dam.py              # 数字资产管理
│   │   ├── upload_handler.py   # 上传处理器
│   │   ├── preprocessor.py     # 视频预处理器
│   │   └── editor.py           # 视频编辑器
│   ├── config.py               # 配置管理
│   ├── main.py                 # 应用入口
│   └── requirements.txt        # 后端依赖
├── frontend/
│   ├── app.py                  # Streamlit UI
│   └── requirements.txt        # 前端依赖
├── start.bat                   # Windows 启动脚本
├── start.sh                    # Linux/Mac 启动脚本
└── .gitignore
```

---

## 🚀 快速开始

### 1. 前置要求

- Python 3.10+
- FFmpeg（必须安装并添加到 PATH）

**安装 FFmpeg:**

```bash
# Windows (使用 winget)
winget install FFmpeg

# Windows (使用 choco)
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 2. 一键启动

**Windows:**
```bash
.\start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

### 3. 手动启动

**启动后端:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**启动前端:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### 4. 访问地址

- **前端 UI**: http://localhost:8501
- **后端 API**: http://localhost:8000
- **Swagger 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## 📡 API 接口

### Upload 上传模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload/single` | 上传单个视频 |
| GET | `/api/upload/list` | 获取上传列表 |

### Assets 资产模块

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/assets/` | 获取资产列表 |
| GET | `/api/assets/{asset_id}` | 获取资产详情 |
| GET | `/api/assets/{asset_id}/logs` | 获取处理日志 |
| DELETE | `/api/assets/{asset_id}` | 删除资产 |

### Processing 处理模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/processing/{asset_id}/preprocess` | 完整预处理 |
| POST | `/api/processing/{asset_id}/metadata` | 提取元数据 |
| POST | `/api/processing/{asset_id}/proxy` | 生成代理文件 |
| POST | `/api/processing/{asset_id}/split` | 分割视频 |

### Editor 编辑模块

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/editor/{asset_id}/clip` | 提取片段 |
| POST | `/api/editor/{asset_id}/rough-cut` | 粗剪合成 |
| POST | `/api/editor/{asset_id}/auto-rough-cut` | 自动粗剪 |

---

## ⚙️ 配置说明

### 环境变量 (`backend/.env`)

```env
# 存储路径
PROCESSING_TEMP_DIR=./temp
FINAL_OUTPUT_DIR=./output
UPLOAD_DIR=./uploads
ASSETS_DIR=./assets

# 存储类型 (local/oss)
STORAGE_TYPE=local

# FFmpeg 路径 (如果不在 PATH 中)
FFMPEG_PATH=ffmpeg

# 服务配置
HOST=0.0.0.0
PORT=8000

# 处理配置
MAX_UPLOAD_SIZE_MB=500
PROXY_RESOLUTION=720
DEFAULT_SEGMENT_DURATION=60

# 日志级别
LOG_LEVEL=INFO
```

---

## 🎬 使用流程

```
1. 上传视频
   └─> 📤 Upload 页面上传 MP4/MOV 等视频文件

2. 预处理
   └─> ⚙️ Processing 页面生成代理/提取元数据

3. 编辑剪辑
   └─> ✂️ Editor 页面进行片段提取或粗剪

4. 查看结果
   └─> 📁 Assets 页面管理输出文件
```

---

## 📂 目录说明

| 目录 | 用途 |
|------|------|
| `uploads/` | 原始上传文件存储 |
| `assets/` | 资产元数据 JSON 文件 |
| `temp/` | 临时处理文件 |
| `output/` | 最终输出文件 |

---

## 📄 许可证

本项目采用 MIT 许可证。

---

<div align="center">

**Made with ❤️ using Python, FastAPI and FFmpeg**

</div>
