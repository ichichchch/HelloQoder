# BatchClip - AI 对话式开发实录

本文档记录了通过与 AI 对话进行 Agentic Coding 开发 BatchClip 项目的完整过程，展示了从需求分析到代码实现的全流程。

---

## 项目起源

**初始需求**: 构建一个自动化视频批量剪辑工具，支持视频上传、预处理、粗剪全流程。

**核心挑战**:
- 需要处理大文件视频上传
- FFmpeg 命令行调用和错误处理
- 数字资产管理（DAM）系统设计
- 前后端分离架构

**技术选型决策**:
- 后端: FastAPI（异步高性能）+ FFmpeg（视频处理）
- 前端: Streamlit（快速原型）
- 存储: 本地文件系统 + JSON 元数据

---

## 对话开发历程

### 第 1 阶段：项目骨架搭建

**用户需求**:
> 创建一个视频批量剪辑工具，需要支持上传、预处理、剪辑功能

**AI 架构设计**:

1. **分层设计**：
   ```
   backend/
   ├── api/           # API 路由层 - 处理 HTTP 请求
   ├── modules/       # 业务模块层 - 核心逻辑
   ├── config.py      # 配置管理
   └── main.py        # 应用入口
   ```

2. **创建配置管理** (`config.py`):
   ```python
   class Settings(BaseSettings):
       # 存储路径
       processing_temp_dir: Path = Path("./temp")
       final_output_dir: Path = Path("./output")
       upload_dir: Path = Path("./uploads")
       assets_dir: Path = Path("./assets")
       
       # FFmpeg 配置
       ffmpeg_path: str = "ffmpeg"
       proxy_resolution: int = 720
       max_upload_size_mb: int = 500
   ```

3. **创建 FastAPI 入口** (`main.py`):
   ```python
   app = FastAPI(
       title="BatchClip API",
       description="Automated video processing pipeline",
       version="0.1.0"
   )
   
   # 生命周期管理
   @asynccontextmanager
   async def lifespan(app: FastAPI):
       settings.ensure_directories()  # 启动时创建必要目录
       yield
   ```

**学到的**: 使用 Pydantic Settings 管理配置，支持 .env 文件和环境变量。

---

### 第 2 阶段：数字资产管理模块

**用户需求**:
> 需要管理上传的视频文件，记录元数据和处理日志

**AI 实现** (`modules/dam.py`):

```python
class AssetManager:
    """数字资产管理器 - 基于 JSON 文件存储"""
    
    def save_metadata(self, asset_id: str, metadata: Dict) -> bool:
        """保存资产元数据到 JSON 文件"""
        asset_dir = self.assets_dir / asset_id
        asset_dir.mkdir(parents=True, exist_ok=True)
        
        metadata["last_updated"] = datetime.now().isoformat()
        
        with open(asset_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def append_log(self, asset_id: str, log_entry: Dict) -> bool:
        """追加处理日志"""
        log_entry["timestamp"] = datetime.now().isoformat()
        # ... 追加到 processing_log.json
    
    def search_by_tags(self, tags: List[str]) -> List[Dict]:
        """按标签搜索资产"""
```

**设计决策**:
- 每个资产独立目录：`assets/{asset_id}/metadata.json`
- 处理日志独立文件：`assets/{asset_id}/processing_log.json`
- 支持标签系统便于检索

---

### 第 3 阶段：文件上传模块

**用户需求**:
> 支持单个和批量视频上传，自动生成唯一 ID

**AI 实现** (`modules/upload_handler.py`):

```python
class UploadHandler:
    async def save_upload(self, file: UploadFile, tags: List[str] = None) -> Dict:
        # 1. 生成唯一 asset_id
        asset_id = str(uuid.uuid4())
        
        # 2. 保存文件到 uploads/{asset_id}/original.mp4
        asset_dir = self.upload_dir / asset_id
        asset_dir.mkdir(parents=True, exist_ok=True)
        file_path = asset_dir / f"original{extension}"
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        # 3. 创建初始元数据
        metadata = {
            "asset_id": asset_id,
            "original_filename": file.filename,
            "size_bytes": len(content),
            "status": "uploaded",
            "tags": tags or []
        }
        
        # 4. 记录上传日志
        self.asset_manager.append_log(asset_id, {
            "event": "upload_complete",
            "original_filename": file.filename
        })
        
        return {"success": True, "asset_id": asset_id}
```

**API 端点** (`api/upload.py`):
```python
@router.post("/single")
async def upload_single_file(
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None)
):
    tag_list = [t.strip() for t in tags.split(",")] if tags else []
    return await upload_handler.save_upload(file, tag_list)

@router.post("/batch")
async def upload_batch_files(files: List[UploadFile] = File(...)):
    # 批量上传支持
```

---

### 第 4 阶段：视频预处理模块

**用户需求**:
> 需要生成代理文件（低分辨率预览）和视频分割功能

**AI 实现** (`modules/preprocessor.py`):

1. **FFprobe 元数据提取**:
```python
def extract_metadata(self, input_path: str) -> Dict:
    cmd = [
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", "-show_streams",
        input_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    probe_data = json.loads(result.stdout)
    
    return {
        "duration": float(format_info.get("duration", 0)),
        "resolution": f"{width}x{height}",
        "fps": video_stream.get("r_frame_rate"),
        "video_codec": video_stream.get("codec_name")
    }
```

2. **代理生成**（720p 低分辨率版本）:
```python
def generate_proxy(self, asset_id: str, input_path: str, resolution: int = 720):
    args = [
        "-i", input_path,
        "-vf", f"scale=-2:{resolution}",  # 保持宽高比
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-y", proxy_path
    ]
    self._run_ffmpeg(args)
```

3. **视频分割**（按时长切分）:
```python
def split_video(self, asset_id: str, input_path: str, segment_duration: int = 60):
    args = [
        "-i", input_path,
        "-c", "copy",
        "-segment_time", str(segment_duration),
        "-f", "segment",
        "-reset_timestamps", "1",
        "segment_%03d.mp4"
    ]
```

**关键设计**:
- 所有 FFmpeg 操作都有日志记录
- 失败时记录错误日志并抛出异常
- 支持组合调用（代理 + 分割）

---

### 第 5 阶段：视频编辑模块

**用户需求**:
> 需要支持片段提取、粗剪合成、自动粗剪

**AI 实现** (`modules/editor.py`):

1. **片段提取**:
```python
def extract_clip(self, asset_id: str, input_path: str, 
                 start_time: float, end_time: float):
    duration = end_time - start_time
    args = [
        "-ss", str(start_time),      # 起始时间
        "-i", input_path,
        "-t", str(duration),          # 持续时间
        "-c", "copy",                 # 直接复制，不重编码
        "-y", output_path
    ]
```

2. **粗剪合成**（多片段拼接）:
```python
def rough_cut(self, asset_id: str, input_path: str, 
              cuts: List[Tuple[float, float]]):
    # 1. 提取每个片段
    clip_paths = []
    for start, end in cuts:
        clip = self.extract_clip(asset_id, input_path, start, end)
        clip_paths.append(clip["output_path"])
    
    # 2. 创建 concat 文件列表
    with open(concat_file, "w") as f:
        for path in clip_paths:
            f.write(f"file '{path}'\n")
    
    # 3. FFmpeg 拼接
    args = [
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c", "copy",
        output_path
    ]
```

3. **自动粗剪**（保留片头片尾）:
```python
def auto_rough_cut(self, asset_id: str, input_path: str,
                   keep_intro_seconds: float = 5.0,
                   keep_outro_seconds: float = 5.0):
    # 自动获取视频时长
    metadata = preprocessor.extract_metadata(input_path)
    duration = metadata["duration"]
    
    # 保留片头和片尾
    cuts = [
        (0, keep_intro_seconds),
        (duration - keep_outro_seconds, duration)
    ]
    
    return self.rough_cut(asset_id, input_path, cuts)
```

---

### 第 6 阶段：Streamlit 前端

**用户需求**:
> 需要一个简单的 UI 来操作这些功能

**AI 实现** (`frontend/app.py`):

```python
# 页面配置
st.set_page_config(
    page_title="BatchClip - Video Processing",
    page_icon="🎬",
    layout="wide"
)

# 侧边栏导航
page = st.sidebar.radio(
    "Navigation",
    ["📤 Upload", "📁 Assets", "⚙️ Processing", "✂️ Editor", "📊 Logs"]
)

# 上传页面
if page == "📤 Upload":
    uploaded_files = st.file_uploader(
        "Select video files",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        accept_multiple_files=True
    )
    
    if st.button("🚀 Upload"):
        for file in uploaded_files:
            result = api_request("POST", "/upload/single", files={...})

# 编辑页面 - 多 Tab 设计
elif page == "✂️ Editor":
    edit_mode = st.tabs(["🎯 Extract Clip", "✂️ Rough Cut", "🤖 Auto Rough Cut"])
    
    with edit_mode[0]:  # 片段提取
        start_time = st.number_input("Start Time (seconds)")
        end_time = st.number_input("End Time (seconds)")
        if st.button("🎬 Extract Clip"):
            api_request("POST", f"/editor/{asset_id}/clip", json={...})
```

**UI 特性**:
- 5 个功能页面（Upload/Assets/Processing/Editor/Logs）
- 实时健康检查显示后端状态
- 动态片段编辑器（支持添加/删除片段）

---

### 第 7 阶段：启动脚本

**用户需求**:
> 需要一键启动前后端

**AI 实现** (`start.bat`):

```batch
@echo off
echo ========================================
echo BatchClip - Video Processing Pipeline
echo ========================================

REM 检查 FFmpeg
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg is not installed
)

REM 启动后端
cd backend
if not exist .venv (python -m venv .venv)
call .venv\Scripts\activate
pip install -r requirements.txt -q
start "BatchClip Backend" cmd /k "uvicorn main:app --reload --port 8000"

REM 启动前端
cd ../frontend
start "BatchClip Frontend" cmd /k "streamlit run app.py --server.port 8501"

echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:8501
```

---

## 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                  Streamlit Frontend                      │
│  ┌────────┐ ┌────────┐ ┌──────────┐ ┌────────┐ ┌──────┐│
│  │ Upload │ │ Assets │ │Processing│ │ Editor │ │ Logs ││
│  └────────┘ └────────┘ └──────────┘ └────────┘ └──────┘│
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP (localhost:8501 → 8000)
┌─────────────────────────▼───────────────────────────────┐
│                   FastAPI Backend                        │
│  ┌───────────────────────────────────────────────────┐  │
│  │                    API Routes                      │  │
│  │   /upload    /assets    /processing    /editor    │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │                 Business Modules                   │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐  │  │
│  │  │AssetManager │ │ Preprocessor│ │   Editor    │  │  │
│  │  │   (DAM)     │ │  (FFmpeg)   │ │  (FFmpeg)   │  │  │
│  │  └─────────────┘ └─────────────┘ └─────────────┘  │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │
┌─────────────────────────▼───────────────────────────────┐
│                    File System                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │
│  │ uploads/ │ │ assets/  │ │  temp/   │ │ output/  │   │
│  │(原始文件)│ │(元数据)  │ │(代理/片段)│ │(最终输出)│   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

### 数据流

```
1. 上传阶段
   User → Upload API → UploadHandler → uploads/{id}/original.mp4
                                     → assets/{id}/metadata.json

2. 预处理阶段
   Processing API → Preprocessor → FFprobe (元数据提取)
                                 → FFmpeg (代理生成: temp/{id}/proxy/)
                                 → FFmpeg (视频分割: temp/{id}/segments/)

3. 编辑阶段
   Editor API → Editor → FFmpeg (片段提取: temp/{id}/clips/)
                       → FFmpeg (拼接合成: output/{id}/roughcut.mp4)
```

### 核心模块职责

| 模块 | 文件 | 职责 | 代码行数 |
|------|------|------|----------|
| AssetManager | `dam.py` | 元数据管理、标签系统、日志记录 | 288 |
| UploadHandler | `upload_handler.py` | 文件上传、asset_id 生成 | 162 |
| Preprocessor | `preprocessor.py` | 代理生成、元数据提取、视频分割 | 363 |
| Editor | `editor.py` | 片段提取、粗剪合成、自动粗剪 | 470 |

### FFmpeg 命令汇总

| 功能 | 命令示例 |
|------|----------|
| 元数据提取 | `ffprobe -v quiet -print_format json -show_format -show_streams input.mp4` |
| 代理生成 | `ffmpeg -i input.mp4 -vf scale=-2:720 -c:v libx264 -preset fast -crf 23 proxy.mp4` |
| 视频分割 | `ffmpeg -i input.mp4 -c copy -segment_time 60 -f segment segment_%03d.mp4` |
| 片段提取 | `ffmpeg -ss 10 -i input.mp4 -t 5 -c copy clip.mp4` |
| 视频拼接 | `ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4` |

---

## API 接口完整列表

### Upload 模块
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/upload/single` | 上传单个视频 |
| POST | `/api/upload/batch` | 批量上传 |
| GET | `/api/upload/list` | 获取上传列表 |
| DELETE | `/api/upload/{asset_id}` | 删除上传 |

### Assets 模块
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/assets/` | 获取资产列表 |
| GET | `/api/assets/{asset_id}` | 获取资产详情 |
| GET | `/api/assets/{asset_id}/logs` | 获取处理日志 |
| DELETE | `/api/assets/{asset_id}` | 删除资产 |

### Processing 模块
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/processing/{asset_id}/preprocess` | 完整预处理 |
| POST | `/api/processing/{asset_id}/metadata` | 提取元数据 |
| POST | `/api/processing/{asset_id}/proxy` | 生成代理 |
| POST | `/api/processing/{asset_id}/split` | 分割视频 |

### Editor 模块
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/editor/{asset_id}/clip` | 提取片段 |
| POST | `/api/editor/{asset_id}/rough-cut` | 粗剪合成 |
| POST | `/api/editor/{asset_id}/auto-rough-cut` | 自动粗剪 |

---

## 总结

### 完成的工作

1. ✅ 项目骨架搭建（FastAPI + 分层架构）
2. ✅ 数字资产管理系统（DAM）
3. ✅ 文件上传模块（单个/批量）
4. ✅ 视频预处理模块（代理/分割/元数据）
5. ✅ 视频编辑模块（片段提取/粗剪/自动粗剪）
6. ✅ Streamlit 前端 UI
7. ✅ 一键启动脚本
8. ✅ 项目文档

### 技术亮点

1. **模块化设计**: API 层与业务层分离，便于测试和维护
2. **全程日志**: 每个处理步骤都有日志记录，便于问题追踪
3. **FFmpeg 封装**: 统一的命令执行和错误处理
4. **JSON 存储**: 轻量级元数据管理，无需数据库
5. **异步上传**: FastAPI 异步处理大文件上传

### 项目统计

| 指标 | 数值 |
|------|------|
| 后端代码 | ~1300 行 |
| 前端代码 | ~530 行 |
| API 端点 | 15 个 |
| 核心模块 | 4 个 |
| 开发阶段 | 7 个 |

---

## 项目信息

| 项目 | 说明 |
|------|------|
| **项目名称** | BatchClip - 自动化视频批量剪辑工具 |
| **开发日期** | 2025-12-26 |
| **开发方式** | Agentic Coding |
| **技术栈** | Python / FastAPI / Streamlit / FFmpeg |
| **存储方式** | 本地文件系统 + JSON 元数据 |

---

<div align="center">

**Made with ❤️ using Python, FastAPI and FFmpeg**

*本文档基于真实项目开发过程编写*

</div>
