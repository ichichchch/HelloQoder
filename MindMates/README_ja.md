# MindMates

<div align="center">

![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?style=flat-square&logo=vue.js)
![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**メンタルヘルス AI コンパニオンプラットフォーム**

*Xiaomi MiMo LLM による 24 時間年中無休のインテリジェント心理カウンセリングサービス*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | 日本語

- **開発ログ**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 機能

- ✅ MiMo LLM ベースのインテリジェント心理カウンセリング対話
- ✅ RAG 強化された専門的メンタルヘルス知識の応答
- ✅ 自動危機検出とヘルプリソースの推奨
- ✅ マルチターン対話コンテキストメモリ
- ✅ セッション履歴の記録と管理
- ✅ JWT ユーザー認証システム
- ✅ Capacitor クロスプラットフォームモバイルサポート (iOS/Android)
- ✅ Docker Compose ワンクリックデプロイ

---

## 🛠️ 技術スタック

| レイヤー | 技術 | バージョン |
|----------|------|------------|
| フロントエンドフレームワーク | Vue + TypeScript + Vite | 3.5+ |
| UI コンポーネント | Element Plus + Tailwind CSS | 2.9+ / 3.4+ |
| モバイルランタイム | Capacitor | 7.0+ |
| ビジネスバックエンド | .NET + Entity Framework Core | 10 |
| AI バックエンド | Python + FastAPI + LangChain | 3.13 / 0.115+ |
| AI モデル | Xiaomi MiMo-V2-Flash | - |
| データベース | PostgreSQL | 17 |
| ベクトルデータベース | Milvus | 2.4+ |
| デプロイ | Docker Compose + Nginx | - |

---

## 🚀 クイックスタート

### 1. 前提条件

- Node.js 20+
- .NET 10 SDK
- Python 3.13+
- PostgreSQL 17

### 2. ワンクリック起動

```bash
# Windows - すべてのサービスを起動
.\start-all.bat

# または個別に起動
.\start-frontend.bat       # http://localhost:5173
.\start-backend-business.bat  # http://localhost:5000
.\start-backend-ai.bat     # http://localhost:8000
```

### 3. Docker デプロイ

```bash
# 環境変数を設定
cp .env.example .env

# すべてのサービスを起動
docker compose up -d
```

---

## 🏗️ プロジェクト構造

```
MindMates/
├── frontend/                 # Vue 3 フロントエンドアプリ
│   ├── src/
│   │   ├── api/             # API クライアント
│   │   ├── views/           # ページコンポーネント
│   │   ├── stores/          # Pinia 状態管理
│   │   └── router/          # ルート設定
│   └── capacitor.config.ts  # モバイル設定
│
├── backend-business/         # .NET ビジネスバックエンド (Clean Architecture)
│   ├── MindMates.Api/       # API レイヤー
│   ├── MindMates.Application/ # アプリケーションレイヤー
│   ├── MindMates.Domain/    # ドメインレイヤー
│   └── MindMates.Infrastructure/ # インフラストラクチャレイヤー
│
└── backend-ai/              # Python AI バックエンド
    ├── app/
    │   ├── memory/          # 対話メモリシステム
    │   ├── services/        # チャットサービス
    │   ├── llm.py           # MiMo LLM 統合
    │   ├── rag.py           # RAG 検索サービス
    │   └── crisis_detector.py # 危機検出
    └── main.py              # FastAPI エントリ
```

---

## ⚙️ 設定

### フロントエンド設定 (`frontend/.env`)

```env
VITE_API_URL=http://localhost:5000
VITE_AI_API_URL=http://localhost:8000
```

### ビジネスバックエンド設定 (`backend-business/appsettings.json`)

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5432;Database=mindmates;Username=..."
  },
  "Jwt": {
    "Secret": "your-secret-key-at-least-32-characters",
    "Issuer": "MindMates",
    "Audience": "MindMates"
  }
}
```

### AI バックエンド設定 (`backend-ai/.env`)

```env
MIMO_API_KEY=your_mimo_api_key
MIMO_API_BASE=https://api.xiaomimimo.com/v1
ZHIPU_API_KEY=your_zhipu_api_key
```

---

## 📡 API エンドポイント

### 認証 API (ビジネスバックエンド)

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| POST | `/api/auth/register` | ユーザー登録 |
| POST | `/api/auth/login` | ユーザーログイン |
| GET | `/api/auth/profile` | ユーザー情報取得 |
| PUT | `/api/auth/profile` | ユーザー情報更新 |

### チャット API (ビジネスバックエンド)

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| GET | `/api/chat/sessions` | セッション一覧取得 |
| POST | `/api/chat/sessions` | 新規セッション作成 |
| GET | `/api/chat/sessions/:id/messages` | メッセージ履歴取得 |
| POST | `/api/chat/sessions/:id/messages` | メッセージ送信 |

### AI API (AI バックエンド)

| メソッド | エンドポイント | 説明 |
|----------|----------------|------|
| POST | `/api/chat` | AI チャットインターフェース |
| GET | `/health` | ヘルスチェック |

---

## 📊 システムアーキテクチャ

```
┌─────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Frontend  │────▶│  Backend-Business │────▶│   Backend-AI    │
│  Vue 3 SPA  │     │   .NET 10 API    │     │ FastAPI + MiMo  │
└─────────────┘     └──────────────────┘     └─────────────────┘
                            │                        │
                            ▼                        ▼
                    ┌──────────────┐         ┌─────────────┐
                    │  PostgreSQL  │         │   Milvus    │
                    └──────────────┘         └─────────────┘
```

---

## ⚠️ メンタルヘルスに関するお知らせ

> 深刻な心理的苦痛を経験されている場合は、速やかに専門的な支援を求めてください。
> 
> **こころの健康相談統一ダイヤル: 0570-064-556**

---

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています。

---

<div align="center">

**Made with ❤️ using Vue 3, .NET 10 and MiMo**

</div>
