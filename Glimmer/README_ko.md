# Glimmer

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![GLM-4V](https://img.shields.io/badge/GLM--4V-Zhipu_AI-2B5697?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**데스크탑 및 모바일 AI 자동화 에이전트**

*Zhipu [Open-AutoGLM](https://github.com/THUDM/OpenAutoGLM) 기반, 데스크탑/Android/iOS/HarmonyOS 크로스 플랫폼 자동화 지원*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | 한국어 | [日本語](./README_ja.md)

</div>

---

## ✨ 기능

- 🖥️ **데스크탑 자동화** - 스크린샷 인식, 마우스 클릭, 키보드 입력
- 📱 **모바일 지원** - Android (ADB), iOS (XCTest), HarmonyOS (HDC)
- 🤖 **AI 기반** - GLM-4V / GPT-4o 비전 모델 기반 화면 이해
- 🎯 **목표 지향** - 자연어로 작업 설명, 자동 실행 단계 계획
- 📸 **실시간 스크린샷** - 각 작업 후 자동 화면 상태 캡처
- 🔄 **단계 제어** - 단일 단계 실행 및 연속 실행 모드 지원
- 🌐 **Web UI** - Vue 3 시각적 제어 패널

---

## 🛠️ 기술 스택

| 레이어 | 기술 | 버전 | 용도 |
|--------|------|------|------|
| 프론트엔드 UI | Vue + TypeScript + Vite | 3.5+ | 시각적 제어 패널 |
| 백엔드 API | Python + HTTP Server | 3.10+ | 에이전트 서비스 |
| 데스크탑 작업 | PyAutoGUI + Pillow | - | 스크린샷 및 입력 시뮬레이션 |
| Android | ADB | - | 기기 제어 |
| iOS | XCTest | - | 기기 제어 |
| HarmonyOS | HDC | - | 기기 제어 |
| AI 모델 | Zhipu GLM-4V | - | 시각적 이해 |

---

## 🏗️ 프로젝트 구조

```
Glimmer/
├── Glimmer-UI/                  # Vue 3 프론트엔드
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel.vue       # 채팅 패널
│   │   │   ├── InputBar.vue        # 입력 바
│   │   │   ├── ScreenshotViewer.vue # 스크린샷 표시
│   │   │   └── StatusIndicator.vue # 상태 표시기
│   │   ├── App.vue
│   │   └── main.ts
│   └── package.json
│
├── Glimmer-Web/                 # Python 백엔드 API
│   ├── core/
│   │   ├── actions/            # 액션 핸들러
│   │   ├── config/             # 구성 및 프롬프트
│   │   ├── desktop/            # 데스크탑 작업 모듈
│   │   ├── model/              # 모델 클라이언트
│   │   └── agent.py            # 에이전트 코어
│   ├── server.py               # HTTP API 서비스
│   └── requirements.txt
│
└── Open-AutoGLM/                # 오픈 소스 자동화 라이브러리
    ├── glimmer/                 # 데스크탑 에이전트
    ├── phone_agent/             # 모바일 에이전트
    │   ├── adb/                 # Android 제어
    │   ├── xctest/              # iOS 제어
    │   └── hdc/                 # HarmonyOS 제어
    ├── glimmer_ui/              # 오리지널 UI
    └── examples/                # 사용 예제
```

---

## 🚀 빠른 시작

### 1. 사전 요구 사항

- Node.js 18+
- Python 3.10+
- Zhipu AI GLM-4V API Key

### 2. 백엔드 서비스 시작

```bash
cd Glimmer-Web
pip install -r requirements.txt
python server.py --host localhost --port 5000
```

### 3. 프론트엔드 UI 시작

```bash
cd Glimmer-UI
npm install
npm run dev
```

또는 원클릭 시작 스크립트 사용:

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

### 4. 접속 URL

- **프론트엔드 UI**: http://localhost:5173
- **백엔드 API**: http://localhost:5000
- **헬스 체크**: http://localhost:5000/api/health

---

## 📡 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/health` | 서비스 상태 확인 |
| GET | `/api/screenshot` | 현재 스크린샷 가져오기 |
| POST | `/api/execute` | 에이전트 단계 실행 |
| POST | `/api/reset` | 에이전트 상태 초기화 |
| POST | `/api/config` | 구성 업데이트 |

### 실행 요청 예시

```json
{
  "goal": "메모장을 열고 Hello World 입력",
  "model_url": "http://localhost:8000/v1",
  "model_name": "glm-4v"
}
```

### 실행 응답 예시

```json
{
  "ui_thought": "바탕 화면이 보입니다, 먼저 시작 메뉴를 열어야 합니다",
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

## ⚙️ 구성

### 모델 구성

`/api/config` 엔드포인트 또는 시작 시 구성:

```json
{
  "model_url": "https://open.bigmodel.cn/api/paas/v4",
  "model_name": "glm-4v",
  "api_key": "your-zhipu-api-key",
  "lang": "ko"
}
```

### 지원되는 모델

| 모델 | 제공자 | 설명 |
|------|--------|------|
| GLM-4V | Zhipu AI | 권장, 우수한 중국어 이해력 |
| GLM-4V-Plus | Zhipu AI | 향상된 버전, 복잡한 시나리오에 적합 |

---

## 📱 모바일 사용

### Android (ADB)

```bash
# adb 기기 연결 확인
adb devices

# phone_agent 사용
cd Open-AutoGLM
python main.py --device android
```

### iOS (XCTest)

[iOS 설정 가이드](./Open-AutoGLM/docs/ios_setup/ios_setup.md) 참조

### HarmonyOS (HDC)

```bash
# hdc 기기 연결 확인
hdc list targets

python main.py --device harmonyos
```

---

## 🎬 사용 예제

```python
from glimmer import GlimmerAgent, AgentConfig
from glimmer.model.client import ModelConfig

# 모델 구성
model_config = ModelConfig(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model_name="glm-4v",
    api_key="your-zhipu-api-key"
)

# 에이전트 생성
agent = GlimmerAgent(model_config, AgentConfig())

# 작업 실행
while True:
    result = agent.step("브라우저를 열고 날씨 검색")
    print(f"생각: {result.thought}")
    print(f"액션: {result.action_type}")
    if result.finished:
        break
```

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다.

---

<div align="center">

**Made with ❤️ using Vue 3, Python and Vision AI**

</div>
