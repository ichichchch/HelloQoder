---
trigger: always_on
---
## Project Overview

**AutoCut** is an internal MVP for validating the automated processing of video files. The core goal is to test the feasibility of an "AI Analysis -> Automated Rough Cut -> Final Video" pipeline for batch processing.

- **Frontend**: Minimalist UI for batch uploads and viewing results (Web or Local).
- **Backend**: A single service for all processing logic using **Python** & **FastAPI**, with **FFmpeg** as the core engine.

## I. Codebase & Structure

### /frontend (Minimal UI)
- **Framework**: TBD (A simple HTML/JS page or a Python-based UI like Streamlit is recommended).
- **Purpose**: Batch video upload, viewing processing logs, and browsing the media asset list.

### /backend (Processing Service)
- **Language**: Python 3.13
- **Framework**: FastAPI
- **Core Engine**: **FFmpeg** (invoked via `subprocess` or a Python wrapper).
- **Architecture**: Service-oriented, with clear modules for:
    - `upload_handler`: Manages incoming files from local or cloud storage.
    - `preprocessor`: Handles proxy generation and video splitting (by time/rules).
    - `editor`: Implements the rule-based rough cutting and stitching logic.
    - `dam` (Digital Asset Management): Manages the file-based metadata, tags, and logs (JSON).

## II. Dependencies

### Frontend
- Dependencies will be minimal and determined by the chosen UI approach.

### Backend (Python)
- `fastapi` & `uvicorn`: Web Server.
- `python-multipart`: For handling file uploads in FastAPI.
- `pydantic`: For data validation and settings management.
- `ffmpeg-python`: (Optional, Recommended) A Python wrapper for FFmpeg.
- `boto3` or `supabase-storage-py`: (Optional) If using AWS S3/OSS or Supabase for cloud storage.

## III. Config & Secrets

### Backend
- **Config**: `.env` file at the root of the `/backend` directory.
- **Rule**: Use Pydantic's `BaseSettings` to load configuration from the `.env` file.
- **Required Vars**:
  - `PROCESSING_TEMP_DIR`: Path for temporary files (e.g., proxies).
  - `FINAL_OUTPUT_DIR`: Path for final rendered videos.
  - `STORAGE_TYPE`: Defines the storage backend, e.g., "local" or "oss".
  - `LOG_LEVEL`: e.g., "INFO", "DEBUG".

## IV. Backing Services

- **Main "Database"**: A file-based system. Processed video metadata, tags, and logs are stored in `.json` files alongside the media files.
- **Storage**: Local filesystem or a cloud storage bucket (OSS / Supabase Storage).

## V. Build & Run

### Frontend
- To be defined based on the chosen framework.

### Backend
- **Setup**: `python -m venv .venv`
- **Activate**: `source .venv/bin/activate` (or `.\venv\Scripts\activate` on Windows)
- **Install**: `pip install -r requirements.txt`
- **Run**: `uvicorn main:app --reload --port 8000`

## VI. Port Binding

- **8000**: Python Backend Service (FastAPI).

## VII. Coding Conventions

- **FFmpeg First**: All video and audio manipulation **must** be done through FFmpeg. Direct invocation is preferred for clarity and control.
- **JSON Logging**: Every processing step for a video (e.g., proxy creation, splitting) must be logged to a corresponding JSON file. The log should be structured and appendable.
- **Asset Metadata**: Every video and generated clip must have an associated JSON file containing its metadata, including duration, resolution, and an array of tags.
- **Rule-Based Logic**: The logic for automatic tagging and cutting (e.g., based on beat detection, labels) must be clearly separated and configurable within the `editor` module.
