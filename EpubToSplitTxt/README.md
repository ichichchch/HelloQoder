# Epub 转文本与章节切分系统

一个专用的 Epub 电子书预处理系统，将 `.epub` 格式电子书转换为纯文本并按章节智能切分为独立的 TXT 文件。

## 功能特性

- ✅ 自动解析 Epub 文件结构并提取纯文本
- ✅ 智能识别章节标题（支持中文、英文格式）
- ✅ 按章节切分为独立 TXT 文件，带序列号保持阅读顺序
- ✅ 支持前言、楔子等特殊章节识别
- ✅ UTF-8 无 BOM 编码输出，确保兼容性
- ✅ 流式处理大文件，内存占用低
- ✅ 可配置的章节匹配规则

## 技术栈

- .NET 9.0
- VersOne.Epub 3.3.0（Epub 解析）
- HtmlAgilityPack 1.11.59（HTML 清洗）
- Microsoft.Extensions.Configuration（配置管理）

## 快速开始

### 1. 编译项目

```bash
dotnet build
```

### 2. 准备 Epub 文件

将你的 `.epub` 电子书文件放入 `RawEpub` 目录：

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

程序会自动生成以下目录结构：

```
EpubToSplitTxt/
├── IntermediateTxt/          # 中间文件（全本文本）
│   ├── 小说1_全本.txt
│   └── 小说2_全本.txt
├── SplitOutput/              # 章节切分输出
│   ├── 小说1/
│   │   ├── 000_楔子.txt
│   │   ├── 001_第一章_重生.txt
│   │   ├── 002_第二章_修炼.txt
│   │   └── ...
│   └── 小说2/
│       └── ...
```

## 配置说明

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

### 配置项说明

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `Splitter:ChapterRegex` | 章节标题匹配正则表达式 | 支持中文数字章节、阿拉伯数字章节等 |
| `Splitter:MinChapterLength` | 最小章节字符数（低于此值会警告） | 100 |
| `Paths:RawEpubFolder` | 原始 Epub 文件存放目录 | `./RawEpub` |
| `Paths:IntermediateTxtFolder` | 全本文本中间文件目录 | `./IntermediateTxt` |
| `Paths:SplitOutputFolder` | 章节切分输出目录 | `./SplitOutput` |

## 章节格式支持

默认支持以下章节标题格式：

- ✅ 中文数字：`第一章`、`第二十章`、`第一百章`
- ✅ 阿拉伯数字：`第1章`、`第001章`
- ✅ 英文格式：`Chapter 1`、`Chapter 2`
- ✅ 特殊章节：`序章`、`楔子`、`引子`、`后记`、`尾声`

如需支持其他格式，可修改 `appsettings.json` 中的 `ChapterRegex` 配置。

## 处理流程

```
[Epub 文件]
    ↓
[EpubConverter] 解析 Epub 结构
    ↓
[清洗 HTML] 移除标签，转换实体
    ↓
[全本文本] 合并为单一 TXT 文件
    ↓
[TextSplitter] 逐行扫描匹配章节
    ↓
[章节文件集] 按序列号输出独立文件
```

## 日志说明

- `[INFO]`：正常处理信息（解析进度、统计数据）
- `[WARN]`：警告信息（章节过小、未匹配到章节等）
- `[ERROR]`：错误信息（文件损坏、I/O 错误等）

## 性能优化

- ✅ 使用预编译正则表达式（`RegexOptions.Compiled`）
- ✅ 流式读取大文本文件（`StreamReader`）
- ✅ 避免一次性加载全文到内存
- ✅ UTF-8 无 BOM 编码，减少文件体积

## 注意事项

1. **编码**：所有输出文件使用 UTF-8 无 BOM 编码
2. **文件名**：自动清洗非法字符，替换为下划线
3. **目录结构**：每本书创建独立子文件夹，避免混淆
4. **正则超时**：章节匹配设置 1 秒超时，防止回溯陷阱

## 系统架构

### 核心组件

- **EpubConverter**：负责解析 Epub 文件并提取纯文本
- **TextSplitter**：负责章节识别与文本切分
- **AppSettings**：配置管理模型

### 依赖关系

```
Program.cs
   ├── EpubConverter (VersOne.Epub, HtmlAgilityPack)
   ├── TextSplitter (System.Text.RegularExpressions)
   └── AppSettings (Microsoft.Extensions.Configuration)
```

## 扩展开发

### 自定义章节匹配规则

修改 `appsettings.json` 中的正则表达式：

```json
{
  "Splitter": {
    "ChapterRegex": "你的自定义正则表达式"
  }
}
```

### 添加新的输出格式

在 `TextSplitter.cs` 中修改 `SplitTextAsync` 方法，支持输出为其他格式（如 Markdown）。

## 许可证

本项目仅供个人学习和研究使用，请遵守相关版权法律法规。

## 贡献

欢迎提交 Issue 和 Pull Request！

---

**开发者**: Qoder AI Assistant  
**版本**: 1.0.0  
**最后更新**: 2025-12-13
