# BatchClip

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![FFmpeg](https://img.shields.io/badge/FFmpeg-Required-007808?style=flat-square&logo=ffmpeg&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**自動バッチビデオ編集ツール**

*FastAPI + FFmpeg + Streamlit アーキテクチャに基づき、ビデオアップロード、前処理、ラフカットワークフローをサポート*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | 日本語

- **開発ログ**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 機能

- 📤 **バッチアップロード** - MP4/MOV/AVI/MKV/WebM などの主要フォーマットをサポート
- 🎞️ **プロキシ生成** - 高速プレビュー用の低解像度プロキシファイルを自動生成
- ✂️ **ビデオ分割** - 長さによる自動ビデオ分割
- 🎬 **クリップ抽出** - 指定時間範囲のセグメントを正確に抽出
- 📋 **ラフカット構成** - 複数のクリップをラフカットビデオに統合
- 🤖 **自動ラフカット** - イントロ/アウトロをインテリジェントに保持して高速プレビュー
- 📁 **アセット管理** - ビデオアセットとメタデータの統合管理
- 📊 **処理ログ** - 処理履歴の完全記録

---

## 🛠️ 技術スタック

| 技術 | バージョン | 用途 |
|------|------------|------|
| Python | 3.10+ | ランタイム環境 |
| FastAPI | 0.109+ | 高性能非同期バックエンド API |
| Streamlit | 1.40+ | フロントエンド UI |
| FFmpeg | - | ビデオ処理エンジン |
| Pydantic | v2 | データ検証と設定 |
| aiofiles | 23.2+ | 非同期ファイル操作 |

---

## 🏗️ プロジェクト構造

```
BatchClip/
├── backend/
│   ├── api/                    # API ルート
│   │   ├── upload.py           # ビデオアップロード API
│   │   ├── assets.py           # アセット管理 API
│   │   ├── processing.py       # 前処理 API
│   │   └── editor.py           # 編集 API
│   ├── modules/                # ビジネスモジュール
│   │   ├── dam.py              # デジタルアセット管理
│   │   ├── upload_handler.py   # アップロードハンドラー
│   │   ├── preprocessor.py     # ビデオプリプロセッサー
│   │   └── editor.py           # ビデオエディター
│   ├── config.py               # 設定管理
│   ├── main.py                 # アプリケーションエントリ
│   └── requirements.txt        # バックエンド依存関係
├── frontend/
│   ├── app.py                  # Streamlit UI
│   └── requirements.txt        # フロントエンド依存関係
├── start.bat                   # Windows 起動スクリプト
├── start.sh                    # Linux/Mac 起動スクリプト
└── .gitignore
```

---

## 🚀 クイックスタート

### 1. 前提条件

- Python 3.10+
- FFmpeg（インストールして PATH に追加必須）

**FFmpeg のインストール:**

```bash
# Windows (winget を使用)
winget install FFmpeg

# Windows (choco を使用)
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### 2. ワンクリック起動

**Windows:**
```bash
.\start.bat
```

**Linux/macOS:**
```bash
chmod +x start.sh
./start.sh
```

### 3. 手動起動

**バックエンド起動:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**フロントエンド起動:**
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

### 4. アクセス URL

- **フロントエンド UI**: http://localhost:8501
- **バックエンド API**: http://localhost:8000
- **Swagger ドキュメント**: http://localhost:8000/docs
- **ヘルスチェック**: http://localhost:8000/health

---

## 📡 API エンドポイント

### アップロードモジュール

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/api/upload/single` | 単一ビデオアップロード |
| GET | `/api/upload/list` | アップロードリスト取得 |

### アセットモジュール

| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/api/assets/` | アセットリスト取得 |
| GET | `/api/assets/{asset_id}` | アセット詳細取得 |
| GET | `/api/assets/{asset_id}/logs` | 処理ログ取得 |
| DELETE | `/api/assets/{asset_id}` | アセット削除 |

### 処理モジュール

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/api/processing/{asset_id}/preprocess` | フル前処理 |
| POST | `/api/processing/{asset_id}/metadata` | メタデータ抽出 |
| POST | `/api/processing/{asset_id}/proxy` | プロキシファイル生成 |
| POST | `/api/processing/{asset_id}/split` | ビデオ分割 |

### エディターモジュール

| メソッド | パス | 説明 |
|----------|------|------|
| POST | `/api/editor/{asset_id}/clip` | クリップ抽出 |
| POST | `/api/editor/{asset_id}/rough-cut` | ラフカット構成 |
| POST | `/api/editor/{asset_id}/auto-rough-cut` | 自動ラフカット |

---

## ⚙️ 設定

### 環境変数 (`backend/.env`)

```env
# ストレージパス
PROCESSING_TEMP_DIR=./temp
FINAL_OUTPUT_DIR=./output
UPLOAD_DIR=./uploads
ASSETS_DIR=./assets

# ストレージタイプ (local/oss)
STORAGE_TYPE=local

# FFmpeg パス (PATH にない場合)
FFMPEG_PATH=ffmpeg

# サービス設定
HOST=0.0.0.0
PORT=8000

# 処理設定
MAX_UPLOAD_SIZE_MB=500
PROXY_RESOLUTION=720
DEFAULT_SEGMENT_DURATION=60

# ログレベル
LOG_LEVEL=INFO
```

---

## 🎬 使用ワークフロー

```
1. ビデオアップロード
   └─> 📤 Upload ページで MP4/MOV などのビデオファイルをアップロード

2. 前処理
   └─> ⚙️ Processing ページでプロキシ生成/メタデータ抽出

3. 編集とクリップ
   └─> ✂️ Editor ページでクリップ抽出またはラフカット

4. 結果確認
   └─> 📁 Assets ページで出力ファイルを管理
```

---

## 📂 ディレクトリ説明

| ディレクトリ | 用途 |
|--------------|------|
| `uploads/` | オリジナルアップロードファイルの保存 |
| `assets/` | アセットメタデータ JSON ファイル |
| `temp/` | 一時処理ファイル |
| `output/` | 最終出力ファイル |

---

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています。

---

<div align="center">

**Made with ❤️ using Python, FastAPI and FFmpeg**

</div>
