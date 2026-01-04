# BatchClip

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Automated Batch Video Editing Tool**

*Based on FastAPI + FFmpeg + Streamlit architecture, supporting video upload, preprocessing, and rough cut workflow*

English | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Development Log**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Features

- 📤 **Batch Upload** - Supports MP4/MOV/AVI/MKV/WebM and other major formats
- 🎞️ **Proxy Generation** - Auto-generate low-resolution proxy files for faster preview
- ✂️ **Video Splitting** - Auto-split long videos by duration
- 🎬 **Clip Extraction** - Extract specific time range segments precisely
- 📋 **Rough Cut Composition** - Merge multiple clips into rough cut video
- 🤖 **Auto Rough Cut** - Intelligently preserve intro/outro for quick preview
- 📁 **Asset Management** - Unified management of video assets and metadata
- 📊 **Processing Logs** - Complete recording of processing history

---

## 🛠️ Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.10+ | Runtime Environment |
| FastAPI | 0.109+ | High-performance Async Backend API |
| Streamlit | 1.40+ | Frontend UI |
| FFmpeg | - | Video Processing Engine |
| Pydantic | v2 | Data Validation & Configuration |
| aiofiles | 23.2+ | Async File Operations |

---

## 🏗️ Project Structure

```
BatchClip/
├── backend/
│   ├── api/                    # API Routes
│   │   ├── upload.py           # Video Upload API
│   │   ├── assets.py           # Asset Management API
│   │   ├── processing.py       # Preprocessing API
│   │   └── editor.py           # Editing API
│   ├── modules/                # Business Modules
│   │   ├── dam.py              # Digital Asset Management
│   │   ├── upload_handler.py   # Upload Handler
│   │   ├── preprocessor.py     # Video Preprocessor
│   │   └── editor.py           # Video Editor
│   ├── config.py               # Configuration Management
│   ├── main.py                 # Application Entry
│   └── requirements.txt        # Backend Dependencies
├── frontend/
│   ├── app.py                  # Streamlit UI
│   └── requirements.txt        # Frontend Dependencies
├── start.bat                   # Windows Startup Script
├── start.sh                    # Linux/Mac Startup Script
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.10+
- FFmpeg (must be installed and added to PATH)

**Install FFmpeg:**

```bash
# Windows (using winget)
winget install FFmpeg

# Windows (using choco)
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 2. One-Click Start

**Windows:**
```bash
.\start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

### 3. Manual Start

**Start Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Start Frontend:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### 4. Access URLs

- **Frontend UI**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

---

## 📡 API Endpoints

### Upload Module

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/upload/single` | Upload single video |
| GET | `/api/upload/list` | Get upload list |

### Assets Module

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/assets/` | Get asset list |
| GET | `/api/assets/{asset_id}` | Get asset details |
| GET | `/api/assets/{asset_id}/logs` | Get processing logs |
| DELETE | `/api/assets/{asset_id}` | Delete asset |

### Processing Module

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/processing/{asset_id}/preprocess` | Full preprocessing |
| POST | `/api/processing/{asset_id}/metadata` | Extract metadata |
| POST | `/api/processing/{asset_id}/proxy` | Generate proxy file |
| POST | `/api/processing/{asset_id}/split` | Split video |

### Editor Module

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/editor/{asset_id}/clip` | Extract clip |
| POST | `/api/editor/{asset_id}/rough-cut` | Rough cut composition |
| POST | `/api/editor/{asset_id}/auto-rough-cut` | Auto rough cut |

---

## ⚙️ Configuration

### Environment Variables (`backend/.env`)

```env
# Storage Paths
PROCESSING_TEMP_DIR=./temp
FINAL_OUTPUT_DIR=./output
UPLOAD_DIR=./uploads
ASSETS_DIR=./assets

# Storage Type (local/oss)
STORAGE_TYPE=local

# FFmpeg Path (if not in PATH)
FFMPEG_PATH=ffmpeg

# Service Configuration
HOST=0.0.0.0
PORT=8000

# Processing Configuration
MAX_UPLOAD_SIZE_MB=500
PROXY_RESOLUTION=720
DEFAULT_SEGMENT_DURATION=60

# Log Level
LOG_LEVEL=INFO
```

---

## 🎬 Usage Workflow

```
1. Upload Video
   └─> 📤 Upload MP4/MOV and other video files on Upload page

2. Preprocess
   └─> ⚙️ Generate proxy/extract metadata on Processing page

3. Edit & Clip
   └─> ✂️ Extract clips or rough cut on Editor page

4. View Results
   └─> 📁 Manage output files on Assets page
```

---

## 📂 Directory Description

| Directory | Purpose |
|-----------|---------|
| `uploads/` | Original uploaded files storage |
| `assets/` | Asset metadata JSON files |
| `temp/` | Temporary processing files |
| `output/` | Final output files |

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Made with ❤️ using Python, FastAPI and FFmpeg**

</div>
