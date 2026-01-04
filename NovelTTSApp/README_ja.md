# NovelTTS

<div align="center">

![.NET](https://img.shields.io/badge/.NET-10.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**小説テキストをオーディオブックに変換する AI アプリケーション**

*Zhipu GLM-TTS による高品質音声合成、Bilibili オーディオ音声クローニングをサポート*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | 日本語

- **開発ログ**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 機能

- 📖 **小説テキスト読み込み** - `.txt`、`.md` ファイルをサポート、URL コンテンツ抽出
- 🎯 **インテリジェントテキスト分割** - TTS に適したセグメントに長いテキストを自動分割
- 🎙️ **AI 音声合成** - Zhipu GLM-TTS ベースの高品質音声生成
- 🎭 **音声クローニング** - Bilibili 動画からリファレンスオーディオを抽出、GLM-TTS-Clone で音声クローン
- 🎵 **オーディオ処理** - NAudio を使用したオーディオ結合とフォーマット変換
- 🔄 **スマートリトライ** - Polly を使用した API 呼び出し失敗時のリトライメカニズム
- 📊 **進捗追跡** - リアルタイム処理進捗表示

---

## 🏗️ アーキテクチャ

プロジェクトは **Clean Architecture** デザインパターンを採用:

```
NovelTTSApp/
├── src/
│   ├── Core/                    # コアレイヤー - ドメインエンティティ＆インターフェース
│   │   ├── Entities/            # ドメインエンティティ
│   │   │   ├── Novel.cs         # 小説エンティティ
│   │   │   ├── AudioSegment.cs  # オーディオセグメントエンティティ
│   │   │   └── VoiceReference.cs# ボイスリファレンスエンティティ
│   │   └── Interfaces/          # コアインターフェース
│   │       ├── INovelReader.cs
│   │       ├── ITextSegmenter.cs
│   │       ├── ITtsService.cs
│   │       ├── IAudioProcessor.cs
│   │       ├── IBilibiliDownloader.cs
│   │       └── INovelProcessor.cs
│   │
│   ├── Infrastructure/          # インフラストラクチャレイヤー - 実装
│   │   ├── Configuration/       # 設定クラス
│   │   ├── Services/            # サービス実装
│   │   │   ├── NovelReader.cs
│   │   │   ├── TextSegmenter.cs
│   │   │   ├── ZhipuTtsService.cs
│   │   │   ├── AudioProcessor.cs
│   │   │   └── BilibiliDownloader.cs
│   │   └── DependencyInjection.cs
│   │
│   └── App/                     # アプリケーションレイヤー - メインプログラム
│       ├── Services/
│       │   └── NovelProcessor.cs
│       ├── Program.cs
│       └── appsettings.json
│
└── NovelTTSApp.sln
```

---

## 🚀 クイックスタート

### 前提条件

- [.NET 10.0 SDK](https://dotnet.microsoft.com/download) 以上
- Zhipu AI API キー ([こちらで取得](https://open.bigmodel.cn/))

### インストールと設定

1. **プロジェクトをクローン**
```bash
git clone https://github.com/your-repo/NovelTTSApp.git
cd NovelTTSApp
```

2. **API キーを設定**

`src/App/appsettings.json` を編集:
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

3. **プロジェクトをビルド**
```bash
dotnet build -c Release
```

4. **プログラムを実行**
```bash
dotnet run --project src/App
```

---

## 📖 使用方法

### コマンドライン引数

```bash
NovelTTSApp [options]

オプション:
    -i, --input <path>     入力小説ファイルパス (.txt または .md)
    -o, --output <path>    出力オーディオファイルパス (.mp3)
    -c, --chapter <name>   チャプターフィルターキーワード
    -v, --voice <url>      音声クローニング用 Bilibili 動画 URL (オプション)
    -h, --help             ヘルプ情報を表示
```

### 使用例

```bash
# デフォルト入力フォルダのすべての小説を処理
dotnet run --project src/App

# 特定のチャプターを処理
dotnet run --project src/App -- -c "第1章"

# Bilibili 動画で音声クローニング使用
dotnet run --project src/App -- -c "第1章" -v https://www.bilibili.com/video/BV1xxxxxxxx

# 単一の小説ファイルを処理
dotnet run --project src/App -- -i ./mynovel.txt -o ./mynovel.mp3
```

---

## 🎭 音声クローニング

音声クローニングは Zhipu GLM-TTS-Clone API で実装、完全なワークフロー:

```
1. Bilibili 動画からリファレンスオーディオをダウンロードして抽出（10 秒クリップ）
2. Zhipu API にオーディオをアップロードして file_id を取得（purpose: voice-clone-input）
3. voice/clone を呼び出して音声を作成 → voice_id を取得
4. voice_id を使用して GLM-TTS を呼び出し、クローン音声を生成
```

> 📚 リファレンス: [GLM-TTS-Clone](https://docs.bigmodel.cn/cn/guide/models/sound-and-video/glm-tts-clone)

---

## 📁 データディレクトリ構造

```
data/
├── novels/              # 小説テキストソースファイル
│   └── BookName/
│       └── 01.Chapter1/
│           ├── 001.Prologue.txt
│           └── 002.Introduction.txt
├── output/              # 生成されたオーディオブックファイル
├── reference_audio/     # Bilibili からのリファレンスオーディオ
└── temp/                # 一時オーディオセグメントファイル
```

---

## 🔧 コア依存関係

| ライブラリ | バージョン | 用途 |
|------------|------------|------|
| Microsoft.Extensions.AI | 最新 | .NET AI 統一抽象化レイヤー |
| NAudio | 2.2.1 | オーディオ処理（フォーマット変換、結合） |
| HtmlAgilityPack | 1.11.59 | HTML パース（Web 小説抽出） |
| Serilog | 4.2.0 | 構造化ログ |
| Polly | 8.0.0 | 復元力（リトライメカニズム） |

---

## 📊 ビジネスフロー

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   アセット準備  │────▶│   テキスト処理  │────▶│    AI 生成      │
│                 │     │                 │     │                 │
│ • 小説読み込み  │     │ • テキスト整理  │     │ • Zhipu API 呼出│
│ • B站 オーディオ│     │ • スマート分割  │     │ • ストリーム処理│
│ • 音声クローン  │     │ • 音声クローン  │     │ • 音声生成      │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                                                         ▼
                                               ┌─────────────────┐
                                               │   後処理        │
                                               │                 │
                                               │ • セグメント結合│
                                               │ • フォーマット変換│
                                               └─────────────────┘
```

---

## 📄 ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています - 詳細は [LICENSE](LICENSE) ファイルを参照してください。

---

<div align="center">

**Made with ❤️ using .NET 10 and Zhipu AI**

</div>
