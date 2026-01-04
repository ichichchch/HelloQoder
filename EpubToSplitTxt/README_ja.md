# EpubToSplitTxt

<div align="center">

![.NET](https://img.shields.io/badge/.NET-9.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Epub 電子書籍テキスト変換・章分割システム**

*`.epub` 形式の電子書籍をプレーンテキストに変換し、章ごとに個別の TXT ファイルにインテリジェントに分割*

[English](./README.md) | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | 日本語

- **開発ログ**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 機能

- ✅ Epub ファイル構造の自動解析とテキスト抽出
- ✅ インテリジェントな章タイトル認識（中国語・英語形式をサポート）
- ✅ 読書順序を維持するシーケンス番号付きの個別 TXT ファイルに章ごとに分割
- ✅ 序章、プロローグなどの特殊章をサポート
- ✅ 互換性のための BOM なし UTF-8 エンコーディング出力
- ✅ 低メモリ使用量での大容量ファイルのストリーム処理
- ✅ 設定可能な章マッチングルール

---

## 🛠️ 技術スタック

| ライブラリ | バージョン | 用途 |
|------------|------------|------|
| .NET | 9.0 | ランタイム環境 |
| VersOne.Epub | 3.3.0 | Epub ファイル解析 |
| HtmlAgilityPack | 1.11.59 | HTML コンテンツクリーニング |
| Microsoft.Extensions.Configuration | - | 設定管理 |

---

## 🚀 クイックスタート

### 1. プロジェクトビルド

```bash
dotnet build
```

### 2. Epub ファイルの準備

`.epub` 電子書籍ファイルを `RawEpub` ディレクトリに配置:

```
EpubToSplitTxt/
├── RawEpub/
│   ├── 小説1.epub
│   └── 小説2.epub
```

### 3. プログラム実行

```bash
dotnet run
```

### 4. 結果確認

プログラムは自動的に以下のディレクトリ構造を生成します:

```
EpubToSplitTxt/
├── IntermediateTxt/          # 中間ファイル（全文テキスト）
│   ├── 小説1_全文.txt
│   └── 小説2_全文.txt
├── SplitOutput/              # 章分割出力
│   ├── 小説1/
│   │   ├── 000_プロローグ.txt
│   │   ├── 001_第1章_転生.txt
│   │   ├── 002_第2章_修練.txt
│   │   └── ...
│   └── 小説2/
│       └── ...
```

---

## ⚙️ 設定

設定ファイル: `appsettings.json`

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

### 設定オプション

| オプション | 説明 | デフォルト |
|------------|------|------------|
| `Splitter:ChapterRegex` | 章タイトルマッチング用正規表現 | 中国語/アラビア数字などをサポート |
| `Splitter:MinChapterLength` | 最小章文字数（下回ると警告） | 100 |
| `Paths:RawEpubFolder` | 元の Epub ファイルディレクトリ | `./RawEpub` |
| `Paths:IntermediateTxtFolder` | 全文中間ファイルディレクトリ | `./IntermediateTxt` |
| `Paths:SplitOutputFolder` | 章分割出力ディレクトリ | `./SplitOutput` |

---

## 📑 サポートされる章形式

デフォルトでサポートされる章タイトル形式:

- ✅ 中国語数字: `第一章`, `第二十章`, `第一百章`
- ✅ アラビア数字: `第1章`, `第001章`
- ✅ 英語形式: `Chapter 1`, `Chapter 2`
- ✅ 特殊章: `序章`, `楔子`, `引子`, `后记`, `尾声`

他の形式をサポートするには、`appsettings.json` の `ChapterRegex` を変更してください。

---

## 📊 処理フロー

```
[Epub ファイル]
    ↓
[EpubConverter] Epub 構造を解析
    ↓
[HTML クリーニング] タグ削除、エンティティ変換
    ↓
[全文テキスト] 単一 TXT ファイルにマージ
    ↓
[TextSplitter] 行スキャンと章マッチング
    ↓
[章ファイル] シーケンス番号付き個別ファイルとして出力
```

---

## 📝 ログ説明

- `[INFO]`: 通常処理情報（解析進捗、統計）
- `[WARN]`: 警告情報（章が小さすぎる、章がマッチしないなど）
- `[ERROR]`: エラー情報（破損ファイル、I/O エラーなど）

---

## ⚡ パフォーマンス最適化

- ✅ プリコンパイル済み正規表現（`RegexOptions.Compiled`）
- ✅ 大容量テキストファイルのストリーム読み取り（`StreamReader`）
- ✅ テキスト全体を一度にメモリに読み込まない
- ✅ ファイルサイズ削減のための BOM なし UTF-8

---

## ⚠️ 注意事項

1. **エンコーディング**: すべての出力ファイルは BOM なし UTF-8 エンコーディングを使用
2. **ファイル名**: 不正文字の自動クリーニング、アンダースコアで置換
3. **ディレクトリ構造**: 混乱を避けるため各書籍に個別のサブフォルダを作成
4. **正規表現タイムアウト**: バックトラッキングトラップ防止のため章マッチングに 1 秒タイムアウト設定

---

## 🏗️ システムアーキテクチャ

### コアコンポーネント

- **EpubConverter**: Epub ファイルの解析とテキスト抽出を担当
- **TextSplitter**: 章認識とテキスト分割を担当
- **AppSettings**: 設定管理モデル

### 依存関係

```
Program.cs
   ├── EpubConverter (VersOne.Epub, HtmlAgilityPack)
   ├── TextSplitter (System.Text.RegularExpressions)
   └── AppSettings (Microsoft.Extensions.Configuration)
```

---

## 🔧 拡張開発

### カスタム章マッチングルール

`appsettings.json` の正規表現を変更:

```json
{
  "Splitter": {
    "ChapterRegex": "カスタム正規表現パターン"
  }
}
```

### 新しい出力形式の追加

`TextSplitter.cs` の `SplitTextAsync` メソッドを変更して他の形式（例: Markdown）をサポート。

---

## 📄 ライセンス

このプロジェクトは個人学習・研究目的のみです。関連する著作権法を遵守してください。

---

## 🤝 貢献

Issue と Pull Request を歓迎します！

---

<div align="center">

**Made with ❤️ using .NET 9 and VersOne.Epub**

</div>
