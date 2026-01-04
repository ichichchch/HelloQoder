# Glimmer 开发对话记录

> 本文档记录了使用 AI Agent 基于智谱 Open-AutoGLM 开源项目构建桌面与移动端 GUI 自动化 Agent 的完整流程。

---

## 第一阶段：项目架构设计

### 用户请求

> 我想基于 Open-AutoGLM 做一个桌面自动化 Agent，支持 Web UI 控制

### AI 分析

分析 Open-AutoGLM 项目结构后，设计了三层架构：

```
Glimmer-UI (Vue 3)
    ↓ (HTTP API)
Glimmer-Web (Python Server)
    ↓ (Core Library)
Open-AutoGLM (原版库)
```

**设计决策：**

| 决策点 | 选择 | 原因 |
|--------|------|------|
| 前端框架 | Vue 3 + TypeScript | 快速开发，类型安全 |
| 后端框架 | Python HTTP Server | 轻量，无额外依赖 |
| 构建工具 | Vite | 开发热重载，构建快速 |
| UI 风格 | 深色渐变主题 | 符合 AI 工具审美 |

---

## 第二阶段：后端 API 服务开发

### 用户请求

> 帮我创建一个 Python 后端，封装 Agent 核心逻辑，提供 REST API

### AI 执行

**创建的文件：**

| 文件 | 说明 |
|------|------|
| `core/agent.py` | GlimmerAgent 主类，封装截图-推理-执行循环 |
| `core/model/client.py` | 模型客户端，支持 GLM-4V API 调用 |
| `core/desktop/screenshot.py` | 截图模块，使用 PyAutoGUI + Pillow |
| `core/actions/handler.py` | 动作处理器，执行点击、输入等操作 |
| `core/config/prompts.py` | 系统提示词，中英文双语支持 |
| `server.py` | HTTP API 服务入口 |

**核心设计 - GlimmerAgent：**

```python
@dataclass
class AgentConfig:
    max_steps: int = 50
    lang: str = "en"
    system_prompt: Optional[str] = None
    verbose: bool = True

class GlimmerAgent:
    def __init__(self, model_config, agent_config, confirmation_callback=None):
        self.model_client = ModelClient(model_config)
        self.action_handler = ActionHandler(...)
    
    def run(self, goal: str) -> str:
        """执行完整任务"""
        while self._step_count < self.agent_config.max_steps:
            result = self._execute_step(goal)
            if result.finished:
                return result.message
    
    def step(self, goal: Optional[str] = None) -> StepResult:
        """单步执行，支持手动控制"""
        return self._execute_step(goal)
```

**API 端点设计：**

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/health` | 检查服务状态 |
| GET | `/api/screenshot` | 获取当前截图 |
| POST | `/api/execute` | 执行 Agent 步骤 |
| POST | `/api/reset` | 重置 Agent 状态 |
| POST | `/api/config` | 更新配置 |

---

## 第三阶段：前端 UI 开发

### 用户请求

> 创建一个 Vue 3 前端界面，左侧显示截图和操作区域，右侧是对话面板

### AI 执行

**创建的组件：**

| 组件 | 说明 |
|------|------|
| `App.vue` | 主应用，管理状态和 API 调用 |
| `ScreenshotViewer.vue` | 截图显示，支持 focus box 高亮 |
| `ChatPanel.vue` | 对话消息列表 |
| `InputBar.vue` | 输入框和发送按钮 |
| `StatusIndicator.vue` | 状态指示器 (idle/working/done/error) |

**状态管理设计：**

```typescript
interface AgentState {
  status: 'idle' | 'working' | 'done' | 'error'
  currentTask: string
  progress: number
}

interface GlimmerResponse {
  ui_thought: string
  ui_focus_box: [number, number, number, number] | null
  status: 'WORKING' | 'DONE' | 'FAIL'
  operation: { action: string; params: object } | null
  screenshot: string
  confidence: string
}
```

**UI 特性：**

- 🎨 深色渐变主题 (Purple/Blue gradient)
- 📸 实时截图显示，支持 focus box 高亮
- 💬 对话式交互，显示 Agent 思考过程
- 🔄 演示模式，无需后端即可体验 UI

---

## 第四阶段：联调与问题修复

### 问题 1：CORS 跨域错误

**错误信息：**
```
Access to fetch at 'http://localhost:5000/api/execute' from origin 'http://localhost:5173' 
has been blocked by CORS policy
```

**解决方案：**

在 `server.py` 中添加 CORS 头：

```python
def _set_headers(self, status_code: int = 200):
    self.send_header("Access-Control-Allow-Origin", "*")
    self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    self.send_header("Access-Control-Allow-Headers", "Content-Type")
```

### 问题 2：截图性能优化

**问题：** 每次截图耗时较长，影响用户体验

**优化方案：**

```python
# 使用 PIL 压缩图片
screenshot = get_screenshot()
# 压缩质量从 95 降到 75
buffer = io.BytesIO()
image.save(buffer, format='JPEG', quality=75)
```

### 问题 3：模型 API 连接失败

**错误信息：**
```
ConnectionError: Unable to connect to http://localhost:8000/v1
```

**排查步骤：**

1. 确认智谱 API Key 配置正确
2. 检查 API 端点地址：`https://open.bigmodel.cn/api/paas/v4`
3. 验证模型名称：`glm-4v`

**修复代码：**

```python
model_config = ModelConfig(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model_name="glm-4v",
    api_key="your-zhipu-api-key",
)
```

---

## 第五阶段：一键启动脚本

### 用户请求

> 帮我创建一键启动脚本，方便快速启动前后端

### AI 执行

**Windows (start.bat):**

```batch
@echo off
echo Starting Glimmer-UI...
cd /d "%~dp0"
call npm install
call npm run dev
```

**Linux/macOS (start.sh):**

```bash
#!/bin/bash
cd "$(dirname "$0")"
npm install
npm run dev
```

---

## 📝 修改的文件清单

| 文件 | 修改内容 | 影响 |
|------|----------|------|
| `Glimmer-Web/core/agent.py` | 实现 GlimmerAgent 主类 | Agent 核心逻辑 |
| `Glimmer-Web/server.py` | 创建 HTTP API 服务 | 后端服务入口 |
| `Glimmer-UI/src/App.vue` | 主应用组件 | 前端入口 |
| `Glimmer-UI/src/components/*.vue` | UI 组件 | 界面交互 |
| `README.md` | 项目文档 | 使用说明 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    Glimmer-UI (Vue 3)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ScreenshotView│  │  ChatPanel   │  │  InputBar    │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │ HTTP API
┌─────────────────────────▼───────────────────────────────┐
│                  Glimmer-Web (Python)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   server.py  │  │   agent.py   │  │  actions     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │ PyAutoGUI / API
┌─────────────────────────▼───────────────────────────────┐
│              Desktop / Mobile Device                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Screenshot  │  │ Mouse/Keyboard│  │ ADB/XCTest  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 💡 关键经验总结

### 1. Agent 循环设计

GUI Agent 的核心是 **感知-思考-行动** 循环：
1. 截图获取当前屏幕状态
2. 发送给视觉模型分析
3. 解析模型返回的动作指令
4. 执行动作并捕获新状态
5. 重复直到任务完成

### 2. 模型响应格式

使用 JSON 格式规范模型输出：

```json
{
  "thought": "我看到了搜索框，需要点击它",
  "action_type": "CLICK",
  "params": {"box_2d": [100, 200, 150, 250]},
  "confidence": "HIGH"
}
```

### 3. 状态管理

前端使用响应式状态管理 Agent 生命周期：
- `idle`: 等待用户输入
- `working`: 正在执行任务
- `done`: 任务完成
- `error`: 执行出错

### 4. 截图优化

- 使用 JPEG 格式而非 PNG（更小体积）
- 适当降低压缩质量（75% 通常足够）
- 考虑缩放大分辨率屏幕的截图

---

## 🚀 后续改进方向

### 1. 功能增强
- **多设备支持**: 整合 Android/iOS 移动端控制
- **历史记录**: 保存任务执行历史供回顾
- **模板任务**: 支持保存常用任务模板

### 2. 性能优化
- **流式响应**: 支持 SSE 流式返回思考过程
- **增量截图**: 只传输变化区域
- **连接复用**: WebSocket 替代 HTTP 轮询

### 3. 用户体验
- **操作确认**: 敏感操作前弹窗确认
- **回退机制**: 支持撤销上一步操作
- **多语言 UI**: 界面语言切换

---

## 🔧 常用调试命令

```bash
# 启动后端服务
cd Glimmer-Web
python server.py --host localhost --port 5000

# 启动前端开发服务
cd Glimmer-UI
npm run dev

# 测试截图功能
python -c "from core.desktop.screenshot import get_screenshot; print(get_screenshot())"

# 检查服务健康状态
curl http://localhost:5000/api/health
```

---

## 总结

### 完成的工作

1. ✅ 设计三层架构 (UI / API / Core)
2. ✅ 实现 GlimmerAgent 核心类
3. ✅ 创建 Python HTTP API 服务
4. ✅ 开发 Vue 3 可视化界面
5. ✅ 解决 CORS 跨域问题
6. ✅ 创建一键启动脚本
7. ✅ 编写项目文档

### 技术要点

- **视觉 AI**: 基于 GLM-4V 视觉模型理解屏幕
- **桌面自动化**: PyAutoGUI 实现鼠标键盘控制
- **现代前端**: Vue 3 + TypeScript + Vite
- **轻量后端**: 纯 Python HTTP Server，无框架依赖
- **组件化 UI**: 可复用的 Vue 组件设计

---

*文档生成时间：2025-01*
