# EpubToSplitTxt

<div align="center">

![.NET](https://img.shields.io/badge/.NET-9.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Epub eBook to Text Conversion and Chapter Splitting System**

*Convert `.epub` format eBooks to plain text and intelligently split into separate TXT files by chapter*

English | [中文](./README_zh.md) | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **Development Log**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ Features

- ✅ Automatically parse Epub file structure and extract plain text
- ✅ Intelligent chapter title recognition (supports Chinese and English formats)
- ✅ Split by chapter into separate TXT files with sequence numbers to maintain reading order
- ✅ Support for special chapters like preface, prologue, etc.
- ✅ UTF-8 without BOM encoding output for compatibility
- ✅ Stream processing for large files with low memory usage
- ✅ Configurable chapter matching rules

---

## 🛠️ Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| .NET | 9.0 | Runtime Environment |
| VersOne.Epub | 3.3.0 | Epub File Parsing |
| HtmlAgilityPack | 1.11.59 | HTML Content Cleaning |
| Microsoft.Extensions.Configuration | - | Configuration Management |

---

## 🚀 Quick Start

### 1. Build Project

```bash
dotnet build
```

### 2. Prepare Epub Files

Place your `.epub` eBook files in the `RawEpub` directory:

```
EpubToSplitTxt/
├── RawEpub/
│   ├── Novel1.epub
│   └── Novel2.epub
```

### 3. Run Program

```bash
dotnet run
```

### 4. View Results

The program will automatically generate the following directory structure:

```
EpubToSplitTxt/
├── IntermediateTxt/          # Intermediate files (full text)
│   ├── Novel1_Full.txt
│   └── Novel2_Full.txt
├── SplitOutput/              # Chapter split output
│   ├── Novel1/
│   │   ├── 000_Prologue.txt
│   │   ├── 001_Chapter1_Rebirth.txt
│   │   ├── 002_Chapter2_Training.txt
│   │   └── ...
│   └── Novel2/
│       └── ...
```

---

## ⚙️ Configuration

Configuration file: `appsettings.json`

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

### Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `Splitter:ChapterRegex` | Regular expression for chapter title matching | Supports Chinese/Arabic numerals, etc. |
| `Splitter:MinChapterLength` | Minimum chapter character count (warns if below) | 100 |
| `Paths:RawEpubFolder` | Raw Epub file directory | `./RawEpub` |
| `Paths:IntermediateTxtFolder` | Full text intermediate file directory | `./IntermediateTxt` |
| `Paths:SplitOutputFolder` | Chapter split output directory | `./SplitOutput` |

---

## 📑 Supported Chapter Formats

Default supported chapter title formats:

- ✅ Chinese numerals: `第一章`, `第二十章`, `第一百章`
- ✅ Arabic numerals: `第1章`, `第001章`
- ✅ English format: `Chapter 1`, `Chapter 2`
- ✅ Special chapters: `序章`, `楔子`, `引子`, `后记`, `尾声`

To support other formats, modify the `ChapterRegex` in `appsettings.json`.

---

## 📊 Processing Flow

```
[Epub File]
    ↓
[EpubConverter] Parse Epub structure
    ↓
[Clean HTML] Remove tags, convert entities
    ↓
[Full Text] Merge into single TXT file
    ↓
[TextSplitter] Scan lines and match chapters
    ↓
[Chapter Files] Output as separate files with sequence numbers
```

---

## 📝 Log Description

- `[INFO]`: Normal processing info (parsing progress, statistics)
- `[WARN]`: Warning info (chapter too small, no chapters matched, etc.)
- `[ERROR]`: Error info (corrupted file, I/O errors, etc.)

---

## ⚡ Performance Optimization

- ✅ Pre-compiled regular expressions (`RegexOptions.Compiled`)
- ✅ Stream reading for large text files (`StreamReader`)
- ✅ Avoid loading entire text into memory at once
- ✅ UTF-8 without BOM encoding to reduce file size

---

## ⚠️ Notes

1. **Encoding**: All output files use UTF-8 without BOM encoding
2. **Filenames**: Automatically clean illegal characters, replace with underscores
3. **Directory Structure**: Create separate subfolder for each book to avoid confusion
4. **Regex Timeout**: Chapter matching has 1-second timeout to prevent backtracking traps

---

## 🏗️ System Architecture

### Core Components

- **EpubConverter**: Responsible for parsing Epub files and extracting plain text
- **TextSplitter**: Responsible for chapter recognition and text splitting
- **AppSettings**: Configuration management model

### Dependencies

```
Program.cs
   ├── EpubConverter (VersOne.Epub, HtmlAgilityPack)
   ├── TextSplitter (System.Text.RegularExpressions)
   └── AppSettings (Microsoft.Extensions.Configuration)
```

---

## 🔧 Extension Development

### Custom Chapter Matching Rules

Modify the regular expression in `appsettings.json`:

```json
{
  "Splitter": {
    "ChapterRegex": "Your custom regex pattern"
  }
}
```

### Add New Output Formats

Modify the `SplitTextAsync` method in `TextSplitter.cs` to support other formats (e.g., Markdown).

---

## 📄 License

This project is for personal learning and research only. Please comply with relevant copyright laws.

---

## 🤝 Contributing

Issues and Pull Requests are welcome!

---

<div align="center">

**Made with ❤️ using .NET 9 and VersOne.Epub**

</div>
