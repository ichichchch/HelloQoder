# EpubToSplitTxt

<div align="center">

![.NET](https://img.shields.io/badge/.NET-9.0-512BD4?style=flat-square&logo=dotnet)
![C#](https://img.shields.io/badge/C%23-13.0-239120?style=flat-square&logo=csharp)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

**Epub 电子书文本转换与章节分割系统**

*将 `.epub` 格式电子书转换为纯文本，并智能按章节分割为独立的 TXT 文件*

[English](./README.md) | 中文 | [Русский](./README_ru.md) | [한국어](./README_ko.md) | [日本語](./README_ja.md)

- **开发过程记录**: [Agent&Chat.md](./docs/Agent&Chat.md)

</div>

---

## ✨ 功能特性

- ✅ 自动解析 Epub 文件结构并提取纯文本
- ✅ 智能章节标题识别（支持中英文格式）
- ✅ 按章节分割为独立 TXT 文件，带序号保持阅读顺序
- ✅ 支持序章、楔子等特殊章节
- ✅ UTF-8 无 BOM 编码输出，兼容性好
- ✅ 流式处理大文件，内存占用低
- ✅ 可配置的章节匹配规则

---

## 🛠️ 技术栈

| 库 | 版本 | 用途 |
|----|------|------|
| .NET | 9.0 | 运行环境 |
| VersOne.Epub | 3.3.0 | Epub 文件解析 |
| HtmlAgilityPack | 1.11.59 | HTML 内容清洗 |
| Microsoft.Extensions.Configuration | - | 配置管理 |

---

## 🚀 快速开始

### 1. 构建项目

```bash
dotnet build
```

### 2. 准备 Epub 文件

将 `.epub` 电子书文件放入 `RawEpub` 目录：

```
EpubToSplitTxt/
├── RawEpub/
│   ├── 小说1.epub
│   └── 小说2.epub
```

### 3. 运行程序

```bash
dotnet run
```

### 4. 查看结果

程序将自动生成以下目录结构：

```
EpubToSplitTxt/
├── IntermediateTxt/          # 中间文件（全文）
│   ├── 小说1_全文.txt
│   └── 小说2_全文.txt
├── SplitOutput/              # 章节分割输出
│   ├── 小说1/
│   │   ├── 000_序章.txt
│   │   ├── 001_第一章_重生.txt
│   │   ├── 002_第二章_修炼.txt
│   │   └── ...
│   └── 小说2/
│       └── ...
```

---

## ⚙️ 配置

配置文件：`appsettings.json`

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

### 配置选项

| 选项 | 说明 | 默认值 |
|------|------|--------|
| `Splitter:ChapterRegex` | 章节标题匹配正则表达式 | 支持中文/阿拉伯数字等 |
| `Splitter:MinChapterLength` | 最小章节字符数（低于则警告） | 100 |
| `Paths:RawEpubFolder` | 原始 Epub 文件目录 | `./RawEpub` |
| `Paths:IntermediateTxtFolder` | 全文中间文件目录 | `./IntermediateTxt` |
| `Paths:SplitOutputFolder` | 章节分割输出目录 | `./SplitOutput` |

---

## 📑 支持的章节格式

默认支持的章节标题格式：

- ✅ 中文数字：`第一章`、`第二十章`、`第一百章`
- ✅ 阿拉伯数字：`第1章`、`第001章`
- ✅ 英文格式：`Chapter 1`、`Chapter 2`
- ✅ 特殊章节：`序章`、`楔子`、`引子`、`后记`、`尾声`

如需支持其他格式，请修改 `appsettings.json` 中的 `ChapterRegex`。

---

## 📊 处理流程

```
[Epub 文件]
    ↓
[EpubConverter] 解析 Epub 结构
    ↓
[清洗 HTML] 移除标签，转换实体
    ↓
[全文] 合并为单个 TXT 文件
    ↓
[TextSplitter] 扫描行并匹配章节
    ↓
[章节文件] 输出带序号的独立文件
```

---

## 📝 日志说明

- `[INFO]`: 正常处理信息（解析进度、统计数据）
- `[WARN]`: 警告信息（章节过小、未匹配到章节等）
- `[ERROR]`: 错误信息（文件损坏、I/O 错误等）

---

## ⚡ 性能优化

- ✅ 预编译正则表达式（`RegexOptions.Compiled`）
- ✅ 大文本文件流式读取（`StreamReader`）
- ✅ 避免一次性将全文加载到内存
- ✅ UTF-8 无 BOM 编码减少文件体积

---

## ⚠️ 注意事项

1. **编码**：所有输出文件使用 UTF-8 无 BOM 编码
2. **文件名**：自动清理非法字符，替换为下划线
3. **目录结构**：每本书创建单独的子文件夹，避免混淆
4. **正则超时**：章节匹配设有 1 秒超时，防止回溯陷阱

---

## 🏗️ 系统架构

### 核心组件

- **EpubConverter**: 负责解析 Epub 文件并提取纯文本
- **TextSplitter**: 负责章节识别和文本分割
- **AppSettings**: 配置管理模型

### 依赖关系

```
Program.cs
   ├── EpubConverter (VersOne.Epub, HtmlAgilityPack)
   ├── TextSplitter (System.Text.RegularExpressions)
   └── AppSettings (Microsoft.Extensions.Configuration)
```

---

## 🔧 扩展开发

### 自定义章节匹配规则

修改 `appsettings.json` 中的正则表达式：

```json
{
  "Splitter": {
    "ChapterRegex": "您的自定义正则表达式"
  }
}
```

### 添加新输出格式

修改 `TextSplitter.cs` 中的 `SplitTextAsync` 方法以支持其他格式（如 Markdown）。

---

## 📄 许可证

本项目仅供个人学习和研究使用。请遵守相关版权法律。

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

<div align="center">

**Made with ❤️ using .NET 9 and VersOne.Epub**

</div>
