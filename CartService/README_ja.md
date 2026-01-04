# Cart Service

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**高性能 E コマースショッピングカートマイクロサービス**

*FastAPI + SQLAlchemy 2.0 非同期アーキテクチャに基づき、ショッピングカートの完全なライフサイクル管理をサポート*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | 日本語

- **開発ログ**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 機能

- 🛒 **カート管理** - カートの作成、照会、クリア
- 📦 **商品操作** - 商品の追加、数量更新、削除
- 🔄 **カート統合** - 匿名カートとユーザーカートの統合をサポート
- ⚡ **非同期アーキテクチャ** - async/await ベースの高性能設計
- 📊 **価格スナップショット** - 商品追加時の単価を記録

---

## 🛠️ 技術スタック

| 技術 | バージョン | 用途 |
|------|------------|------|
| Python | 3.10+ | ランタイム環境 |
| FastAPI | 0.109+ | 高性能非同期 Web フレームワーク |
| PostgreSQL | 15+ | リレーショナルデータベース |
| SQLAlchemy | 2.0+ | 非同期 ORM |
| Pydantic | v2 | データ検証 |
| Alembic | 1.13+ | データベースマイグレーション |

---

## 🏗️ プロジェクト構造

```
cart-service/
├── app/
│   ├── api/v1/endpoints/    # API ルート
│   ├── core/                # 設定管理
│   ├── db/                  # データベース接続
│   ├── models/              # ORM モデル
│   ├── schemas/             # Pydantic モデル
│   ├── services/            # ビジネスロジックレイヤー
│   └── main.py              # アプリケーションエントリ
├── alembic/                 # データベースマイグレーションスクリプト
├── .env.example             # 環境変数テンプレート
├── alembic.ini              # Alembic 設定
└── requirements.txt         # 依存関係
```

---

## 🚀 クイックスタート

### 1. 依存関係のインストール

```bash
cd projects/cart-service
pip install -r requirements.txt
```

### 2. データベース設定

PostgreSQL データベースを作成:

```sql
CREATE DATABASE cart_db;
```

環境変数を設定:

```bash
copy .env.example .env
# .env ファイルを編集して正しいデータベース接続情報を設定
```

### 3. データベースマイグレーション

```bash
alembic upgrade head
```

### 4. サービス起動

```bash
uvicorn app.main:app --reload
```

### 5. API アクセス

- **Swagger ドキュメント**: http://127.0.0.1:8000/docs
- **ReDoc ドキュメント**: http://127.0.0.1:8000/redoc
- **ヘルスチェック**: http://127.0.0.1:8000/health

---

## 📡 API エンドポイント

| メソッド | パス | 説明 |
|----------|------|------|
| GET | `/api/v1/carts/{cart_id}` | カート詳細取得 |
| POST | `/api/v1/carts` | カート作成 |
| POST | `/api/v1/carts/{cart_id}/items` | 商品追加 |
| PATCH | `/api/v1/carts/{cart_id}/items/{item_id}` | 商品数量更新 |
| DELETE | `/api/v1/carts/{cart_id}/items/{item_id}` | 商品削除 |
| DELETE | `/api/v1/carts/{cart_id}` | カートクリア |
| POST | `/api/v1/carts/{cart_id}/merge` | カート統合 |

---

## 🗃️ データモデル

### carts テーブル

| フィールド | 型 | 説明 |
|------------|------|------|
| id | UUID | プライマリキー |
| user_id | UUID | ユーザー ID (null 可) |
| status | VARCHAR | ステータス |
| created_at | DATETIME | 作成日時 |
| updated_at | DATETIME | 更新日時 |

### cart_items テーブル

| フィールド | 型 | 説明 |
|------------|------|------|
| id | UUID | プライマリキー |
| cart_id | UUID | カート ID |
| product_id | VARCHAR | 商品 SKU |
| quantity | INTEGER | 数量 |
| unit_price | DECIMAL | 単価 |
| added_at | DATETIME | 追加日時 |

---

## 📖 開発ドキュメント

- [AI Agent 開発ガイド](./Agent.md) - 技術スタック制約と開発標準

---

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています。

---

<div align="center">

**Made with ❤️ using Python and FastAPI**

</div>
