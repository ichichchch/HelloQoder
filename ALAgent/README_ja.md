# AL Agent

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6?style=flat-square&logo=typescript&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**自律コーディングエージェント VS Code 拡張機能**

*[Cline](https://github.com/cline/cline) にインスパイアされた、マルチモーダル RAG 技術を活用した高度な AI コーディングアシスタント*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | 日本語

- **開発ログ**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 機能

- 🤖 **インテリジェントコードエージェント** - 自然言語による自律コーディング
- 📚 **マルチモーダル RAG** - セマンティック検索とグラフベースクエリによる強化検索
- 🔧 **ツール呼び出し** - ファイル操作、コード分析、システムコマンド
- 🌐 **マルチソースローディング** - Web ページ、GitHub リポジトリ、PDF からのインデックス作成
- 💬 **コンテキスト認識チャット** - 正確な応答のための会話コンテキスト維持

---

## 🏗️ アーキテクチャ

```
AL Agent
├── frontend-extension/    # VS Code 拡張機能 (TypeScript + React + Vite)
├── backend-agent/         # 推論エンジン (.NET 10 + Microsoft Agent Framework)
└── backend-rag/          # RAG サービス (Python 3.13 + LangChain + LightRAG)
```

---

## 🛠️ 技術スタック

| レイヤー | 技術 | バージョン | 用途 |
|----------|------|------------|------|
| フロントエンド | TypeScript + React + Vite | 5.0+ | VS Code 拡張機能 |
| エージェントバックエンド | .NET + Microsoft Agent Framework | 10.0 | 推論エンジン |
| RAG バックエンド | Python + FastAPI + LangChain | 3.13 | セマンティック検索 |
| ベクトル DB | Milvus | 2.4+ | エンベディング保存 |
| AI モデル | OpenAI / DashScope | - | LLM とエンベディング |

---

## 🚀 クイックスタート

### 前提条件

- Node.js 18+
- .NET 10 SDK
- Python 3.11+ と uv パッケージマネージャー
- OpenAI または DashScope API キー
- Milvus ベクトルデータベース（オプション、本番環境用）

### 1. フロントエンド拡張機能

```bash
cd frontend-extension
npm install
npm run watch  # 開発用ホットリロード
```

デバッグ: VS Code で `F5` を押してデバッグモードで拡張機能を起動。

### 2. エージェントバックエンド (.NET)

```bash
cd backend-agent
# appsettings.json または環境変数で API キーを設定
dotnet run --urls=http://localhost:5000
```

### 3. RAG バックエンド (Python)

```bash
cd backend-rag
uv venv                    # 仮想環境の作成
source .venv/bin/activate  # Windows: .venv\Scripts\activate
uv pip install -e .        # 開発モードでインストール

# 環境設定（コピーして編集）
cp .env.example .env
# .env に API キーを設定 (DASHSCOPE_API_KEY または OPENAI_API_KEY)

# サービス実行
fastapi dev app/main.py --port 8000
```

---

## 🌐 ポート設定

| サービス | ポート | 説明 |
|----------|--------|------|
| .NET Agent API | 5000 | プロンプト受信、ツール呼び出し返却 |
| Python RAG API | 8000 | クエリ受信、コードチャンク返却 |
| VS Code 拡張機能 | 内部 | Webview 通信 |

---

## ⚙️ 設定

### VS Code 設定

```json
{
  "alagent.agentApiUrl": "http://localhost:5000",
  "alagent.ragApiUrl": "http://localhost:8000",
  "alagent.openaiApiKey": ""  // VS Code secrets に安全に保存
}
```

### 環境変数

**エージェントバックエンド (.NET):**
- `Agent__OpenAIApiKey`: OpenAI API キー（または appsettings.json を使用）
- `Agent__ModelId`: 使用するモデル（デフォルト: gpt-4o）
- `Agent__RagApiUrl`: RAG サービス URL（デフォルト: http://localhost:8000）

**RAG バックエンド (Python):**
- `DASHSCOPE_API_KEY`: Qwen エンベディング用 DashScope API キー（推奨）
- `OPENAI_API_KEY`: フォールバック用 OpenAI API キー
- `MILVUS_HOST/MILVUS_PORT`: ベクトル DB 接続（デフォルト: localhost:19530）
- `TEXT_EMBEDDING_MODEL`: エンベディングモデル（デフォルト: text-embedding-v4）
- `LIGHTRAG_QUERY_MODE`: クエリモード（naive/local/global/hybrid/mix）

---

## 📡 API エンドポイント

**RAG サービス**: http://localhost:8000
- `/` - API ドキュメント
- `/health` - ヘルスチェック
- `/api/query` - セマンティック検索
- `/api/index` - ワークスペースのインデックス作成
- `/api/load/web` - Web ページの読み込み
- `/api/load/github` - GitHub リポジトリの読み込み
- `/api/load/pdf` - PDF の読み込み
- `/api/lightrag/query` - グラフベース検索

---

## 🧪 テスト

### RAG 検索テスト

```bash
cd backend-rag
python scripts/evaluate_recall.py --workspace /path/to/test/workspace
```

成功基準: Recall@5 > 0.8

---

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています。

---

<div align="center">

**Made with ❤️ using .NET 10, Python, and Vision AI**

</div>
