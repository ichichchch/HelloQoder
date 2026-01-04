# EpubToSplitTxt

<div align="center">

![.NET](https://img.shields.io/badge/.NET-9.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Epub 전자책 텍스트 변환 및 챕터 분할 시스템**

*`.epub` 형식의 전자책을 일반 텍스트로 변환하고 챕터별로 개별 TXT 파일로 지능적으로 분할*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | 한국어 | [日本語](./README_ja.md)

- **개발 로그**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 기능

- ✅ Epub 파일 구조 자동 파싱 및 텍스트 추출
- ✅ 지능형 챕터 제목 인식 (중국어 및 영어 형식 지원)
- ✅ 읽기 순서를 유지하는 시퀀스 번호가 있는 개별 TXT 파일로 챕터별 분할
- ✅ 서문, 프롤로그 등 특수 챕터 지원
- ✅ 호환성을 위한 BOM 없는 UTF-8 인코딩 출력
- ✅ 낮은 메모리 사용량으로 대용량 파일 스트림 처리
- ✅ 구성 가능한 챕터 매칭 규칙

---

## 🛠️ 기술 스택

| 라이브러리 | 버전 | 용도 |
|------------|------|------|
| .NET | 9.0 | 런타임 환경 |
| VersOne.Epub | 3.3.0 | Epub 파일 파싱 |
| HtmlAgilityPack | 1.11.59 | HTML 콘텐츠 정리 |
| Microsoft.Extensions.Configuration | - | 구성 관리 |

---

## 🚀 빠른 시작

### 1. 프로젝트 빌드

```bash
dotnet build
```

### 2. Epub 파일 준비

`.epub` 전자책 파일을 `RawEpub` 디렉토리에 배치:

```
EpubToSplitTxt/
├── RawEpub/
│   ├── 소설1.epub
│   └── 소설2.epub
```

### 3. 프로그램 실행

```bash
dotnet run
```

### 4. 결과 확인

프로그램은 자동으로 다음 디렉토리 구조를 생성합니다:

```
EpubToSplitTxt/
├── IntermediateTxt/          # 중간 파일 (전체 텍스트)
│   ├── 소설1_전체.txt
│   └── 소설2_전체.txt
├── SplitOutput/              # 챕터 분할 출력
│   ├── 소설1/
│   │   ├── 000_프롤로그.txt
│   │   ├── 001_제1장_환생.txt
│   │   ├── 002_제2장_수련.txt
│   │   └── ...
│   └── 소설2/
│       └── ...
```

---

## ⚙️ 구성

구성 파일: `appsettings.json`

```json
{
  "Splitter": {
    "ChapterRegex": "(^第[0-9一二三四五六七八九十百千]+[章节卷].*)|(^Chapter [0-9]+.*)|(^序章.*)|(^楔子.*)|(^引子.*)|(^后记.*)|(^尾声.*)",
    "MinChapterLength": 100
  },
  "Paths": {
    "RawEpubFolder": "./RawEpub",
    "IntermediateTxtFolder": "./IntermediateTxt",
    "SplitOutputFolder": "./SplitOutput"
  }
}
```

### 구성 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `Splitter:ChapterRegex` | 챕터 제목 매칭용 정규 표현식 | 중국어/아라비아 숫자 등 지원 |
| `Splitter:MinChapterLength` | 최소 챕터 문자 수 (미만 시 경고) | 100 |
| `Paths:RawEpubFolder` | 원본 Epub 파일 디렉토리 | `./RawEpub` |
| `Paths:IntermediateTxtFolder` | 전체 텍스트 중간 파일 디렉토리 | `./IntermediateTxt` |
| `Paths:SplitOutputFolder` | 챕터 분할 출력 디렉토리 | `./SplitOutput` |

---

## 📑 지원되는 챕터 형식

기본 지원 챕터 제목 형식:

- ✅ 중국어 숫자: `第一章`, `第二十章`, `第一百章`
- ✅ 아라비아 숫자: `第1章`, `第001章`
- ✅ 영어 형식: `Chapter 1`, `Chapter 2`
- ✅ 특수 챕터: `序章`, `楔子`, `引子`, `后记`, `尾声`

다른 형식을 지원하려면 `appsettings.json`의 `ChapterRegex`를 수정하세요.

---

## 📊 처리 흐름

```
[Epub 파일]
    ↓
[EpubConverter] Epub 구조 파싱
    ↓
[HTML 정리] 태그 제거, 엔티티 변환
    ↓
[전체 텍스트] 단일 TXT 파일로 병합
    ↓
[TextSplitter] 라인 스캔 및 챕터 매칭
    ↓
[챕터 파일] 시퀀스 번호 있는 개별 파일로 출력
```

---

## 📝 로그 설명

- `[INFO]`: 정상 처리 정보 (파싱 진행률, 통계)
- `[WARN]`: 경고 정보 (챕터가 너무 작음, 챕터 매칭 없음 등)
- `[ERROR]`: 오류 정보 (손상된 파일, I/O 오류 등)

---

## ⚡ 성능 최적화

- ✅ 미리 컴파일된 정규 표현식 (`RegexOptions.Compiled`)
- ✅ 대용량 텍스트 파일의 스트림 읽기 (`StreamReader`)
- ✅ 전체 텍스트를 한 번에 메모리에 로드하지 않음
- ✅ 파일 크기 감소를 위한 BOM 없는 UTF-8

---

## ⚠️ 주의 사항

1. **인코딩**: 모든 출력 파일은 BOM 없는 UTF-8 인코딩 사용
2. **파일 이름**: 잘못된 문자 자동 정리, 밑줄로 대체
3. **디렉토리 구조**: 혼란을 피하기 위해 각 책에 대해 별도의 하위 폴더 생성
4. **정규식 타임아웃**: 백트래킹 트랩 방지를 위해 챕터 매칭에 1초 타임아웃 설정

---

## 🏗️ 시스템 아키텍처

### 핵심 구성 요소

- **EpubConverter**: Epub 파일 파싱 및 텍스트 추출 담당
- **TextSplitter**: 챕터 인식 및 텍스트 분할 담당
- **AppSettings**: 구성 관리 모델

### 의존성

```
Program.cs
   ├── EpubConverter (VersOne.Epub, HtmlAgilityPack)
   ├── TextSplitter (System.Text.RegularExpressions)
   └── AppSettings (Microsoft.Extensions.Configuration)
```

---

## 🔧 확장 개발

### 사용자 정의 챕터 매칭 규칙

`appsettings.json`의 정규 표현식 수정:

```json
{
  "Splitter": {
    "ChapterRegex": "사용자 정의 정규 표현식 패턴"
  }
}
```

### 새 출력 형식 추가

`TextSplitter.cs`의 `SplitTextAsync` 메서드를 수정하여 다른 형식 (예: Markdown) 지원.

---

## 📄 라이선스

이 프로젝트는 개인 학습 및 연구 목적으로만 사용됩니다. 관련 저작권법을 준수해 주세요.

---

## 🤝 기여

Issue와 Pull Request를 환영합니다!

---

<div align="center">

**Made with ❤️ using .NET 9 and VersOne.Epub**

</div>
