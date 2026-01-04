# Cart Service

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**고성능 이커머스 장바구니 마이크로서비스**

*FastAPI + SQLAlchemy 2.0 비동기 아키텍처 기반, 장바구니 전체 라이프사이클 관리 지원*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | 한국어 | [日本語](./README_ja.md)

- **개발 로그**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 기능

- 🛒 **장바구니 관리** - 장바구니 생성, 조회, 비우기
- 📦 **상품 작업** - 상품 추가, 수량 업데이트, 제거
- 🔄 **장바구니 병합** - 익명 장바구니와 사용자 장바구니 병합 지원
- ⚡ **비동기 아키텍처** - async/await 기반 고성능 설계
- 📊 **가격 스냅샷** - 상품 추가 시점의 단가 기록

---

## 🛠️ 기술 스택

| 기술 | 버전 | 용도 |
|------|------|------|
| Python | 3.10+ | 런타임 환경 |
| FastAPI | 0.109+ | 고성능 비동기 웹 프레임워크 |
| PostgreSQL | 15+ | 관계형 데이터베이스 |
| SQLAlchemy | 2.0+ | 비동기 ORM |
| Pydantic | v2 | 데이터 검증 |
| Alembic | 1.13+ | 데이터베이스 마이그레이션 |

---

## 🏗️ 프로젝트 구조

```
cart-service/
├── app/
│   ├── api/v1/endpoints/    # API 라우트
│   ├── core/                # 구성 관리
│   ├── db/                  # 데이터베이스 연결
│   ├── models/              # ORM 모델
│   ├── schemas/             # Pydantic 모델
│   ├── services/            # 비즈니스 로직 레이어
│   └── main.py              # 애플리케이션 진입점
├── alembic/                 # 데이터베이스 마이그레이션 스크립트
├── .env.example             # 환경 변수 템플릿
├── alembic.ini              # Alembic 구성
└── requirements.txt         # 의존성
```

---

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
cd projects/cart-service
pip install -r requirements.txt
```

### 2. 데이터베이스 구성

PostgreSQL 데이터베이스 생성:

```sql
CREATE DATABASE cart_db;
```

환경 변수 구성:

```bash
copy .env.example .env
# .env 파일을 편집하여 올바른 데이터베이스 연결 정보 설정
```

### 3. 데이터베이스 마이그레이션

```bash
alembic upgrade head
```

### 4. 서비스 시작

```bash
uvicorn app.main:app --reload
```

### 5. API 접속

- **Swagger 문서**: http://127.0.0.1:8000/docs
- **ReDoc 문서**: http://127.0.0.1:8000/redoc
- **헬스 체크**: http://127.0.0.1:8000/health

---

## 📡 API 엔드포인트

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/v1/carts/{cart_id}` | 장바구니 상세 조회 |
| POST | `/api/v1/carts` | 장바구니 생성 |
| POST | `/api/v1/carts/{cart_id}/items` | 상품 추가 |
| PATCH | `/api/v1/carts/{cart_id}/items/{item_id}` | 상품 수량 업데이트 |
| DELETE | `/api/v1/carts/{cart_id}/items/{item_id}` | 상품 제거 |
| DELETE | `/api/v1/carts/{cart_id}` | 장바구니 비우기 |
| POST | `/api/v1/carts/{cart_id}/merge` | 장바구니 병합 |

---

## 🗃️ 데이터 모델

### carts 테이블

| 필드 | 타입 | 설명 |
|------|------|------|
| id | UUID | 기본 키 |
| user_id | UUID | 사용자 ID (null 가능) |
| status | VARCHAR | 상태 |
| created_at | DATETIME | 생성 시간 |
| updated_at | DATETIME | 업데이트 시간 |

### cart_items 테이블

| 필드 | 타입 | 설명 |
|------|------|------|
| id | UUID | 기본 키 |
| cart_id | UUID | 장바구니 ID |
| product_id | VARCHAR | 상품 SKU |
| quantity | INTEGER | 수량 |
| unit_price | DECIMAL | 단가 |
| added_at | DATETIME | 추가 시간 |

---

## 📖 개발 문서

- [AI Agent 개발 가이드](./Agent.md) - 기술 스택 제약 및 개발 표준

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다.

---

<div align="center">

**Made with ❤️ using Python and FastAPI**

</div>
