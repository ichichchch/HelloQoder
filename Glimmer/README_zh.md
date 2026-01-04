# Glimmer

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![GLM-4V](https://img.shields.io/badge/GLM--4V-智谱AI-2B5697?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**桌面与移动端 AI 自动化 Agent**

*基于智谱 [Open-AutoGLM](https://github.com/THUDM/OpenAutoGLM) 开源项目，支持桌面/Android/iOS/HarmonyOS 全平台自动化操作*

[English](./README.md) | 中文 | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

</div>

---

## ✨ 功能特性

- 🖥️ **桌面自动化** - 截图识别、鼠标点击、键盘输入
- 📱 **移动端支持** - Android (ADB)、iOS (XCTest)、HarmonyOS (HDC)
- 🤖 **AI 驱动** - 基于 GLM-4V / GPT-4o 视觉模型理解屏幕
- 🎯 **目标导向** - 自然语言描述任务，自动规划执行步骤
- 📸 **实时截图** - 每步操作后自动获取屏幕状态
- 🔄 **步进控制** - 支持单步执行和连续运行模式
- 🌐 **Web UI** - Vue 3 可视化操作界面

---

## 🛠️ 技术栈

| 层级 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 前端 UI | Vue + TypeScript + Vite | 3.5+ | 可视化控制面板 |
| 后端 API | Python + HTTP Server | 3.10+ | Agent 服务 |
| 桌面操作 | PyAutoGUI + Pillow | - | 截图与输入模拟 |
| Android | ADB | - | 设备控制 |
| iOS | XCTest | - | 设备控制 |
| HarmonyOS | HDC | - | 设备控制 |
| AI 模型 | 智谱 GLM-4V | - | 视觉理解 |

---

## 🏗️ 项目结构

```
Glimmer/
├── Glimmer-UI/                  # Vue 3 前端界面
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel.vue       # 对话面板
│   │   │   ├── InputBar.vue        # 输入栏
│   │   │   ├── ScreenshotViewer.vue # 截图显示
│   │   │   └── StatusIndicator.vue # 状态指示
│   │   ├── App.vue
│   │   └── main.ts
│   └── package.json
│
├── Glimmer-Web/                 # Python 后端 API
│   ├── core/
│   │   ├── actions/            # 动作处理器
│   │   ├── config/             # 配置与提示词
│   │   ├── desktop/            # 桌面操作模块
│   │   ├── model/              # 模型客户端
│   │   └── agent.py            # Agent 核心
│   ├── server.py               # HTTP API 服务
│   └── requirements.txt
│
└── Open-AutoGLM/                # 开源自动化库
    ├── glimmer/                 # 桌面 Agent
    ├── phone_agent/             # 移动端 Agent
    │   ├── adb/                 # Android 控制
    │   ├── xctest/              # iOS 控制
    │   └── hdc/                 # HarmonyOS 控制
    ├── glimmer_ui/              # 原版 UI
    └── examples/                # 使用示例
```

---

## 🚀 快速开始

### 1. 前置要求

- Node.js 18+
- Python 3.10+
- 智谱 AI GLM-4V API Key

### 2. 启动后端服务

```bash
cd Glimmer-Web
pip install -r requirements.txt
python server.py --host localhost --port 5000
```

### 3. 启动前端界面

```bash
cd Glimmer-UI
npm install
npm run dev
```

或使用一键启动脚本：

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

### 4. 访问地址

- **前端 UI**: http://localhost:5173
- **后端 API**: http://localhost:5000
- **健康检查**: http://localhost:5000/api/health

---

## 📡 API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 检查服务状态 |
| GET | `/api/screenshot` | 获取当前截图 |
| POST | `/api/execute` | 执行 Agent 步骤 |
| POST | `/api/reset` | 重置 Agent 状态 |
| POST | `/api/config` | 更新配置 |

### 执行请求示例

```json
{
  "goal": "打开记事本并输入 Hello World",
  "model_url": "http://localhost:8000/v1",
  "model_name": "glm-4v"
}
```

### 执行响应示例

```json
{
  "ui_thought": "我看到了桌面，需要先打开开始菜单",
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

## ⚙️ 配置说明

### 模型配置

通过 `/api/config` 接口或启动时配置：

```json
{
  "model_url": "https://open.bigmodel.cn/api/paas/v4",
  "model_name": "glm-4v",
  "api_key": "your-zhipu-api-key",
  "lang": "zh"
}
```

### 支持的模型

| 模型 | 提供商 | 说明 |
|------|--------|------|
| GLM-4V | 智谱 AI | 推荐，中文理解优秀 |
| GLM-4V-Plus | 智谱 AI | 增强版，复杂场景更佳 |

---

## 📱 移动端使用

### Android (ADB)

```bash
# 确保 adb 已连接设备
adb devices

# 使用 phone_agent
cd Open-AutoGLM
python main.py --device android
```

### iOS (XCTest)

参考 [iOS 设置指南](./Open-AutoGLM/docs/ios_setup/ios_setup.md)

### HarmonyOS (HDC)

```bash
# 确保 hdc 已连接设备
hdc list targets

python main.py --device harmonyos
```

---

## 🎬 使用示例

```python
from glimmer import GlimmerAgent, AgentConfig
from glimmer.model.client import ModelConfig

# 配置模型
model_config = ModelConfig(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model_name="glm-4v",
    api_key="your-zhipu-api-key"
)

# 创建 Agent
agent = GlimmerAgent(model_config, AgentConfig())

# 执行任务
while True:
    result = agent.step("打开浏览器搜索天气")
    print(f"思考: {result.thought}")
    print(f"动作: {result.action_type}")
    if result.finished:
        break
```

---

## 📄 许可证

本项目采用 MIT 许可证。

---

<div align="center">

**Made with ❤️ using Vue 3, Python and Vision AI**

</div>
