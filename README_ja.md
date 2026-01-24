# HelloQoder

<div align="center">

![Projects](https://img.shields.io/badge/Projects-6-blue?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![.NET](https://img.shields.io/badge/.NET-9.0%20|%2010.0-512BD4?style=flat-square&logo=dotnet)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

**Qoder が作成したプロジェクトコレクション**

*AI 駆動のエージェンティックコーディング実践*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | 日本語

</div>

---

## 📂 プロジェクト一覧

| プロジェクト | 説明 | 技術スタック | ステータス |
|--------------|------|--------------|------------|
| [Glimmer](./Glimmer/) | デスクトップ＆モバイル AI 自動化エージェント | Vue 3, Python, Zhipu GLM-4V | ✅ Active |
| [CartService](./CartService/) | E コマースショッピングカートマイクロサービス | FastAPI, PostgreSQL, SQLAlchemy | ✅ Active |
| [NovelTTSApp](./NovelTTSApp/) | 小説をオーディオブックに変換する AI アプリ | .NET 10, Zhipu GLM-TTS, NAudio | ✅ Active |
| [EpubToSplitTxt](./EpubToSplitTxt/) | Epub 電子書籍チャプター分割ツール | .NET 9, VersOne.Epub | ✅ Active |
| [MindMates](./MindMates/) | メンタルヘルス AI コンパニオンプラットフォーム | Vue 3, .NET 10, FastAPI, MiMo | ✅ Active |
| [BatchClip](./BatchClip/) | 自動バッチビデオ編集ツール | FastAPI, Streamlit, FFmpeg | ✅ Active |

---

## 🏗️ ディレクトリ構造

```
HelloQoder/
├── Glimmer/                 # 🖥️ デスクトップ AI 自動化
│   ├── Glimmer-UI/          # Vue 3 フロントエンド
│   ├── Glimmer-Web/         # Python バックエンド
│   ├── Open-AutoGLM/        # オープンソース自動化ライブラリ
│   └── README.md            # プロジェクトドキュメント
│
├── CartService/             # 🛒 ショッピングカートマイクロサービス
│   ├── app/                 # アプリケーションコード
│   ├── alembic/             # データベースマイグレーション
│   └── README.md            # プロジェクトドキュメント
│
├── NovelTTSApp/             # 🎙️ 小説音声変換アプリ
│   ├── src/
│   │   ├── Core/            # コアレイヤー - ドメインエンティティ＆インターフェース
│   │   ├── Infrastructure/  # インフラストラクチャレイヤー - 実装
│   │   └── App/             # アプリケーションレイヤー - メインプログラム
│   └── README.md            # プロジェクトドキュメント
│
├── EpubToSplitTxt/          # 📖 Epub 分割ツール
│   ├── EpubConverter.cs     # Epub パーサー
│   ├── TextSplitter.cs      # チャプター分割器
│   └── README.md            # プロジェクトドキュメント
│
├── MindMates/               # 🧠 メンタルヘルス AI プラットフォーム
│   ├── frontend/            # Vue 3 フロントエンド
│   ├── backend-business/    # .NET 10 ビジネスバックエンド
│   ├── backend-ai/          # Python AI バックエンド
│   └── README.md            # プロジェクトドキュメント
│
├── BatchClip/               # 🎬 バッチビデオ編集ツール
│   ├── backend/             # FastAPI バックエンド
│   ├── frontend/            # Streamlit フロントエンド
│   └── start.bat            # 起動スクリプト
│
└── README.md                # このファイル
```

---

## ✨ クイックナビゲーション

### 🖥️ Glimmer

デスクトップ＆モバイル AI 自動化エージェント、Zhipu Open-AutoGLM ベース、クロスプラットフォーム自動化をサポート。

- **技術スタック**: Vue 3 / Python 3.10+ / PyAutoGUI / Zhipu GLM-4V
- **機能**: デスクトップ自動化、モバイルサポート (Android/iOS/HarmonyOS)、AI ビジュアル理解
- **アーキテクチャ**: Vue フロントエンド + Python エージェントサービス
- **ドキュメント**: [詳細を見る](./Glimmer/README.md)

---

### 🛒 CartService

高性能 E コマースショッピングカートマイクロサービス、カート CRUD、商品管理、カート統合をサポート。

- **技術スタック**: Python 3.10+ / FastAPI / PostgreSQL / SQLAlchemy 2.0
- **機能**: カート管理、商品 CRUD、カート統合
- **ドキュメント**: [詳細を見る](./CartService/README.md)

---

### 🎙️ NovelTTSApp

小説テキストをオーディオブックに変換する AI アプリ、Zhipu GLM-TTS で高品質音声合成。

- **技術スタック**: .NET 10 / C# 13 / Zhipu GLM-TTS / NAudio
- **機能**: 小説テキスト読み込み、スマート分割、AI 音声合成、音声クローニング
- **アーキテクチャ**: Clean Architecture
- **ドキュメント**: [詳細を見る](./NovelTTSApp/README.md)

---

### 📖 EpubToSplitTxt

Epub 電子書籍前処理システム、`.epub` をテキストに変換し、インテリジェントなチャプター分割。

- **技術スタック**: .NET 9 / VersOne.Epub / HtmlAgilityPack
- **機能**: Epub パース、チャプター認識、スマート分割、UTF-8 出力
- **ドキュメント**: [詳細を見る](./EpubToSplitTxt/README.md)

---

### 🧠 MindMates

メンタルヘルス AI コンパニオンプラットフォーム、24 時間年中無休のインテリジェント心理カウンセリングサービス。

- **技術スタック**: Vue 3 + TypeScript / .NET 10 / Python FastAPI / MiMo
- **機能**: AI チャット、危機検出、RAG 強化、モバイルサポート
- **アーキテクチャ**: フロントエンド・バックエンド分離 + AI マイクロサービス
- **ドキュメント**: [詳細を見る](./MindMates/README.md)

---

### 🎬 BatchClip

自動バッチビデオ編集ツール、AI が素材を分析し、自動でラフカットビデオを生成。

- **技術スタック**: Python / FastAPI / Streamlit / FFmpeg
- **機能**: ビデオアップロード、AI 素材分析、自動ラフカット、バッチ処理
- **アーキテクチャ**: フロントエンド・バックエンド分離
- **ドキュメント**: [詳細を見る](./BatchClip/README.md)

---

## 🔧 技術スタック概要

| 分野 | 技術 |
|------|------|
| **バックエンドサービス** | Python, FastAPI, .NET 10 |
| **フロントエンド** | Vue 3, TypeScript, Vite |
| **AI 統合** | Zhipu GLM-TTS, Zhipu GLM-4V, Xiaomi MiMo, LangChain, LightRAG |
| **データベース** | PostgreSQL, Milvus |
| **ビデオ処理** | FFmpeg |
| **デプロイ** | Docker Compose |

---

## 📋 新規プロジェクトの追加

1. ルートディレクトリに新しいプロジェクトフォルダを作成
2. プロジェクトコードと独立した `README.md` を追加
3. オプション: `Agent.md` と `Agent&Chat.md` を追加
4. このファイルのプロジェクト一覧を更新

---

<div align="center">

**Made with ❤️ by Qoder**

</div>
