# Glimmer

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![GLM-4V](https://img.shields.io/badge/GLM--4V-Zhipu_AI-2B5697?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**デスクトップ＆モバイル AI 自動化エージェント**

*Zhipu [Open-AutoGLM](https://github.com/THUDM/OpenAutoGLM) ベース、デスクトップ/Android/iOS/HarmonyOS クロスプラットフォーム自動化をサポート*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | 日本語

</div>

---

## ✨ 機能

- 🖥️ **デスクトップ自動化** - スクリーンショット認識、マウスクリック、キーボード入力
- 📱 **モバイルサポート** - Android (ADB)、iOS (XCTest)、HarmonyOS (HDC)
- 🤖 **AI 駆動** - GLM-4V / GPT-4o ビジョンモデルベースの画面理解
- 🎯 **目標指向** - 自然言語でタスクを記述、自動で実行ステップを計画
- 📸 **リアルタイムスクリーンショット** - 各アクション後に自動で画面状態をキャプチャ
- 🔄 **ステップ制御** - シングルステップ実行と連続実行モードをサポート
- 🌐 **Web UI** - Vue 3 ビジュアルコントロールパネル

---

## 🛠️ 技術スタック

| レイヤー | 技術 | バージョン | 用途 |
|----------|------|------------|------|
| フロントエンド UI | Vue + TypeScript + Vite | 3.5+ | ビジュアルコントロールパネル |
| バックエンド API | Python + HTTP Server | 3.10+ | エージェントサービス |
| デスクトップ操作 | PyAutoGUI + Pillow | - | スクリーンショットと入力シミュレーション |
| Android | ADB | - | デバイス制御 |
| iOS | XCTest | - | デバイス制御 |
| HarmonyOS | HDC | - | デバイス制御 |
| AI モデル | Zhipu GLM-4V | - | ビジュアル理解 |

---

## 🏗️ プロジェクト構造

```
Glimmer/
├── Glimmer-UI/                  # Vue 3 フロントエンド
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatPanel.vue       # チャットパネル
│   │   │   ├── InputBar.vue        # 入力バー
│   │   │   ├── ScreenshotViewer.vue # スクリーンショット表示
│   │   │   └── StatusIndicator.vue # ステータスインジケーター
│   │   ├── App.vue
│   │   └── main.ts
│   └── package.json
│
├── Glimmer-Web/                 # Python バックエンド API
│   ├── core/
│   │   ├── actions/            # アクションハンドラー
│   │   ├── config/             # 設定とプロンプト
│   │   ├── desktop/            # デスクトップ操作モジュール
│   │   ├── model/              # モデルクライアント
│   │   └── agent.py            # エージェントコア
│   ├── server.py               # HTTP API サービス
│   └── requirements.txt
│
└── Open-AutoGLM/                # オープンソース自動化ライブラリ
    ├── glimmer/                 # デスクトップエージェント
    ├── phone_agent/             # モバイルエージェント
    │   ├── adb/                 # Android 制御
    │   ├── xctest/              # iOS 制御
    │   └── hdc/                 # HarmonyOS 制御
    ├── glimmer_ui/              # オリジナル UI
    └── examples/                # 使用例
```

---

## 🚀 クイックスタート

### 1. 前提条件

- Node.js 18+
- Python 3.10+
- Zhipu AI GLM-4V API キー

### 2. バックエンドサービス起動

```bash
cd Glimmer-Web
pip install -r requirements.txt
python server.py --host localhost --port 5000
```

### 3. フロントエンド UI 起動

```bash
cd Glimmer-UI
npm install
npm run dev
```

またはワンクリック起動スクリプトを使用:

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

### 4. アクセス URL

- **フロントエンド UI**: http://localhost:5173
- **バックエンド API**: http://localhost:5000
- **ヘルスチェック**: http://localhost:5000/api/health

---

## 📡 API エンドポイント

| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/api/health` | サービスステータス確認 |
| GET | `/api/screenshot` | 現在のスクリーンショット取得 |
| POST | `/api/execute` | エージェントステップ実行 |
| POST | `/api/reset` | エージェント状態リセット |
| POST | `/api/config` | 設定更新 |

### 実行リクエスト例

```json
{
  "goal": "メモ帳を開いて Hello World と入力",
  "model_url": "http://localhost:8000/v1",
  "model_name": "glm-4v"
}
```

### 実行レスポンス例

```json
{
  "ui_thought": "デスクトップが見えます、まずスタートメニューを開く必要があります",
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

## ⚙️ 設定

### モデル設定

`/api/config` エンドポイントまたは起動時に設定:

```json
{
  "model_url": "https://open.bigmodel.cn/api/paas/v4",
  "model_name": "glm-4v",
  "api_key": "your-zhipu-api-key",
  "lang": "ja"
}
```

### サポートされるモデル

| モデル | プロバイダー | 説明 |
|--------|--------------|------|
| GLM-4V | Zhipu AI | 推奨、優れた中国語理解 |
| GLM-4V-Plus | Zhipu AI | 拡張版、複雑なシナリオに最適 |

---

## 📱 モバイルでの使用

### Android (ADB)

```bash
# adb デバイスが接続されていることを確認
adb devices

# phone_agent を使用
cd Open-AutoGLM
python main.py --device android
```

### iOS (XCTest)

[iOS セットアップガイド](./Open-AutoGLM/docs/ios_setup/ios_setup.md) を参照

### HarmonyOS (HDC)

```bash
# hdc デバイスが接続されていることを確認
hdc list targets

python main.py --device harmonyos
```

---

## 🎬 使用例

```python
from glimmer import GlimmerAgent, AgentConfig
from glimmer.model.client import ModelConfig

# モデル設定
model_config = ModelConfig(
    base_url="https://open.bigmodel.cn/api/paas/v4",
    model_name="glm-4v",
    api_key="your-zhipu-api-key"
)

# エージェント作成
agent = GlimmerAgent(model_config, AgentConfig())

# タスク実行
while True:
    result = agent.step("ブラウザを開いて天気を検索")
    print(f"思考: {result.thought}")
    print(f"アクション: {result.action_type}")
    if result.finished:
        break
```

---

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています。

---

<div align="center">

**Made with ❤️ using Vue 3, Python and Vision AI**

</div>
