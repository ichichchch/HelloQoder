# Glimmer

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![GLM-4V](https://img.shields.io/badge/GLM--4V-Zhipu_AI-2B5697?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Desktop and Mobile AI Automation Agent**

*Based on Zhipu [Open-AutoGLM](https://github.com/THUDM/OpenAutoGLM), supporting desktop/Android/iOS/HarmonyOS cross-platform automation*

English | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

</div>

---

## ✨ Features

- 🖥️ **Desktop Automation** - Screenshot recognition, mouse clicks, keyboard input
- 📱 **Mobile Support** - Android (ADB), iOS (XCTest), HarmonyOS (HDC)
- 🤖 **AI Driven** - Screen understanding based on GLM-4V / GPT-4o vision models
- 🎯 **Goal Oriented** - Describe tasks in natural language, auto-plan execution steps
- 📸 **Real-time Screenshots** - Auto-capture screen state after each action
- 🔄 **Step Control** - Support single-step execution and continuous run modes
- 🌐 **Web UI** - Vue 3 visual control panel

---

## 🛠️ Tech Stack

| Layer | Technology | Version | Purpose |
|-------|------------|---------|---------|
| Frontend UI | Vue + TypeScript + Vite | 3.5+ | Visual Control Panel |
| Backend API | Python + HTTP Server | 3.10+ | Agent Service |
| Desktop Ops | PyAutoGUI + Pillow | - | Screenshots and Input Simulation |
| Android | ADB | - | Device Control |
| iOS | XCTest | - | Device Control |
| HarmonyOS | HDC | - | Device Control |
| AI Model | Zhipu GLM-4V | - | Visual Understanding |

---

## 🏗️ Project Structure

```
Glimmer/
├── Glimmer-UI/                  # Vue 3 Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel.vue       # Chat Panel
│   │   │   ├── InputBar.vue        # Input Bar
│   │   │   ├── ScreenshotViewer.vue # Screenshot Display
│   │   │   └── StatusIndicator.vue # Status Indicator
│   │   ├── App.vue
│   │   └── main.ts
│   └── package.json
│
├── Glimmer-Web/                 # Python Backend API
│   ├── core/
│   │   ├── actions/            # Action Handlers
│   │   ├── config/             # Config and Prompts
│   │   ├── desktop/            # Desktop Operations Module
│   │   ├── model/              # Model Client
│   │   └── agent.py            # Agent Core
│   ├── server.py               # HTTP API Service
│   └── requirements.txt
│
└── Open-AutoGLM/                # Open Source Automation Library
    ├── glimmer/                 # Desktop Agent
    ├── phone_agent/             # Mobile Agent
    │   ├── adb/                 # Android Control
    │   ├── xctest/              # iOS Control
    │   └── hdc/                 # HarmonyOS Control
    ├── glimmer_ui/              # Original UI
    └── examples/                # Usage Examples
```

---

## 🚀 Quick Start

### 1. Prerequisites

- Node.js 18+
- Python 3.10+
- Zhipu AI GLM-4V API Key

### 2. Start Backend Service

```bash
cd Glimmer-Web
pip install -r requirements.txt
python server.py --host localhost --port 5000
```

### 3. Start Frontend UI

```bash
cd Glimmer-UI
npm install
npm run dev
```

Or use one-click startup scripts:

**Windows:**
```bash
cd Glimmer-UI
.\start.bat
```

**Linux/macOS:**
```bash
cd Glimmer-UI
chmod +x start.sh && ./start.sh
```

### 4. Access URLs

- **Frontend UI**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **Health Check**: http://localhost:5000/api/health

---

## 📡 API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Check service status |
| GET | `/api/screenshot` | Get current screenshot |
| POST | `/api/execute` | Execute agent step |
| POST | `/api/reset` | Reset agent state |
| POST | `/api/config` | Update configuration |

### Execute Request Example

```json
{
  "goal": "Open Notepad and type Hello World",
  "model_url": "http://localhost:8000/v1",
  "model_name": "glm-4v"
}
```

### Execute Response Example

```json
{
  "ui_thought": "I see the desktop, need to open the start menu first",
  "ui_focus_box": [100, 200, 150, 250],
  "status": "WORKING",
  "operation": {
    "action": "click",
    "params": {"x": 125, "y": 225}
  },
  "screenshot": "base64...",
  "confidence": 0.95
}
```

---

## ⚙️ Configuration

### Model Configuration

Configure via `/api/config` endpoint or at startup:

```json
{
  "model_url": "https://open.bigmodel.cn/api/paas/v4",
  "model_name": "glm-4v",
  "api_key": "your-zhipu-api-key",
  "lang": "en"
}
```

### Supported Models

| Model | Provider | Description |
|-------|----------|-------------|
| GLM-4V | Zhipu AI | Recommended, excellent Chinese understanding |
| GLM-4V-Plus | Zhipu AI | Enhanced version, better for complex scenarios |

---

## 📱 Mobile Usage

### Android (ADB)

```bash
# Ensure adb device is connected
adb devices

# Use phone_agent
cd Open-AutoGLM
python main.py --device android
```

### iOS (XCTest)

See [iOS Setup Guide](./Open-AutoGLM/docs/ios_setup/ios_setup.md)

### HarmonyOS (HDC)

```bash
# Ensure hdc device is connected
hdc list targets

python main.py --device harmonyos
```

---

## 🎬 Usage Example

```python
from glimmer import GlimmerAgent, AgentConfig
from glimmer.model.client import ModelConfig

# Configure model
model_config = ModelConfig(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model_name="glm-4v",
    api_key="your-zhipu-api-key"
)

# Create agent
agent = GlimmerAgent(model_config, AgentConfig())

# Execute task
while True:
    result = agent.step("Open browser and search for weather")
    print(f"Thought: {result.thought}")
    print(f"Action: {result.action_type}")
    if result.finished:
        break
```

---

## 📄 License

This project is licensed under the MIT License.

---

<div align="center">

**Made with ❤️ using Vue 3, Python and Vision AI**

</div>
