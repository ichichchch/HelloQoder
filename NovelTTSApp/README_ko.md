# NovelTTS

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**소설 텍스트를 오디오북으로 변환하는 AI 애플리케이션**

*Zhipu GLM-TTS를 사용한 고품질 음성 합성, Bilibili 오디오 음성 클로닝 지원*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | 한국어 | [日本語](./README_ja.md)

- **개발 로그**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 기능

- 📖 **소설 텍스트 읽기** - `.txt`, `.md` 파일 지원, URL 콘텐츠 추출
- 🎯 **지능형 텍스트 분할** - TTS에 적합한 세그먼트로 긴 텍스트 자동 분할
- 🎙️ **AI 음성 합성** - Zhipu GLM-TTS 기반 고품질 음성 생성
- 🎭 **음성 클로닝** - Bilibili 비디오에서 참조 오디오 추출, GLM-TTS-Clone으로 음성 클로닝
- 🎵 **오디오 처리** - NAudio를 사용한 오디오 병합 및 형식 변환
- 🔄 **스마트 재시도** - Polly를 사용한 API 호출 실패 시 재시도 메커니즘
- 📊 **진행률 추적** - 실시간 처리 진행률 표시

---

## 🏗️ 아키텍처

프로젝트는 **Clean Architecture** 디자인 패턴 채택:

```
NovelTTSApp/
├── src/
│   ├── Core/                    # 코어 레이어 - 도메인 엔티티 및 인터페이스
│   │   ├── Entities/            # 도메인 엔티티
│   │   │   ├── Novel.cs         # 소설 엔티티
│   │   │   ├── AudioSegment.cs  # 오디오 세그먼트 엔티티
│   │   │   └── VoiceReference.cs# 음성 참조 엔티티
│   │   └── Interfaces/          # 코어 인터페이스
│   │       ├── INovelReader.cs
│   │       ├── ITextSegmenter.cs
│   │       ├── ITtsService.cs
│   │       ├── IAudioProcessor.cs
│   │       ├── IBilibiliDownloader.cs
│   │       └── INovelProcessor.cs
│   │
│   ├── Infrastructure/          # 인프라 레이어 - 구현
│   │   ├── Configuration/       # 구성 클래스
│   │   ├── Services/            # 서비스 구현
│   │   │   ├── NovelReader.cs
│   │   │   ├── TextSegmenter.cs
│   │   │   ├── ZhipuTtsService.cs
│   │   │   ├── AudioProcessor.cs
│   │   │   └── BilibiliDownloader.cs
│   │   └── DependencyInjection.cs
│   │
│   └── App/                     # 애플리케이션 레이어 - 메인 프로그램
│       ├── Services/
│       │   └── NovelProcessor.cs
│       ├── Program.cs
│       └── appsettings.json
│
└── NovelTTSApp.sln
```

---

## 🚀 빠른 시작

### 사전 요구 사항

- [.NET 10.0 SDK](https://dotnet.microsoft.com/download) 이상
- Zhipu AI API Key ([여기서 받기](https://open.bigmodel.cn/))

### 설치 및 구성

1. **프로젝트 클론**
```bash
git clone https://github.com/your-repo/NovelTTSApp.git
cd NovelTTSApp
```

2. **API Key 구성**

`src/App/appsettings.json` 편집:
```json
{
  "AI": {
    "Endpoint": "https://open.bigmodel.cn/api/paas/v4/",
    "ApiKey": "YOUR_API_KEY_HERE",
    "ModelId": "glm-4-voice"
  },
  "Paths": {
    "InputFolder": "./data/novels",
    "OutputFolder": "./data/output",
    "ReferenceAudioFolder": "./data/reference_audio",
    "TempFolder": "./data/temp"
  }
}
```

3. **프로젝트 빌드**
```bash
dotnet build -c Release
```

4. **프로그램 실행**
```bash
dotnet run --project src/App
```

---

## 📖 사용법

### 명령줄 인수

```bash
NovelTTSApp [options]

옵션:
    -i, --input <path>     입력 소설 파일 경로 (.txt 또는 .md)
    -o, --output <path>    출력 오디오 파일 경로 (.mp3)
    -c, --chapter <name>   챕터 필터 키워드
    -v, --voice <url>      음성 클로닝용 Bilibili 비디오 URL (선택 사항)
    -h, --help             도움말 정보 표시
```

### 사용 예제

```bash
# 기본 입력 폴더의 모든 소설 처리
dotnet run --project src/App

# 특정 챕터 처리
dotnet run --project src/App -- -c "제1장"

# Bilibili 비디오로 음성 클로닝 사용
dotnet run --project src/App -- -c "제1장" -v https://www.bilibili.com/video/BV1xxxxxxxx

# 단일 소설 파일 처리
dotnet run --project src/App -- -i ./mynovel.txt -o ./mynovel.mp3
```

---

## 🎭 음성 클로닝

음성 클로닝은 Zhipu GLM-TTS-Clone API를 통해 구현, 전체 워크플로우:

```
1. Bilibili 비디오에서 참조 오디오 다운로드 및 추출 (10초 클립)
2. Zhipu API에 오디오 업로드하여 file_id 획득 (purpose: voice-clone-input)
3. voice/clone 호출하여 음성 생성 → voice_id 획득
4. voice_id를 사용하여 GLM-TTS 호출, 클로닝된 음성 생성
```

> 📚 참조: [GLM-TTS-Clone](https://docs.bigmodel.cn/cn/guide/models/sound-and-video/glm-tts-clone)

---

## 📁 데이터 디렉토리 구조

```
data/
├── novels/              # 소설 텍스트 소스 파일
│   └── BookName/
│       └── 01.Chapter1/
│           ├── 001.Prologue.txt
│           └── 002.Introduction.txt
├── output/              # 생성된 오디오북 파일
├── reference_audio/     # Bilibili에서 추출한 참조 오디오
└── temp/                # 임시 오디오 세그먼트 파일
```

---

## 🔧 핵심 의존성

| 라이브러리 | 버전 | 용도 |
|------------|------|------|
| Microsoft.Extensions.AI | 최신 | .NET AI 통합 추상화 레이어 |
| NAudio | 2.2.1 | 오디오 처리 (형식 변환, 병합) |
| HtmlAgilityPack | 1.11.59 | HTML 파싱 (웹 소설 추출) |
| Serilog | 4.2.0 | 구조화된 로깅 |
| Polly | 8.0.0 | 복원력 (재시도 메커니즘) |

---

## 📊 비즈니스 흐름

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    자산 준비    │────▶│   텍스트 처리   │────▶│    AI 생성      │
│                 │     │                 │     │                 │
│ • 소설 읽기     │     │ • 텍스트 정리   │     │ • Zhipu API 호출│
│ • B站 오디오    │     │ • 스마트 분할   │     │ • 스트림 처리   │
│ • 음성 클론 준비│     │ • 음성 클론     │     │ • 음성 생성     │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │    후처리       │
                                               │                 │
                                               │ • 세그먼트 병합 │
                                               │ • 형식 변환     │
                                               └─────────────────┘
```

---

## 📄 라이선스

이 프로젝트는 MIT 라이선스에 따라 라이선스가 부여됩니다 - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

---

<div align="center">

**Made with ❤️ using .NET 10 and Zhipu AI**

</div>
