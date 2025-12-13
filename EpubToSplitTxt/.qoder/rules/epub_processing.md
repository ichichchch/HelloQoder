---
trigger: always_on
alwaysApply: true
---
## Codebase (代码库基础)
告知 Agent 本模块专注于预处理逻辑，需保持与主项目架构一致：

- **语言**: C# (.NET 10 Preview)
- **职责边界**:
    - `EpubConverter`: 负责解析 `.epub` 文件结构并提取纯文本。
    - `TextSplitter`: 负责基于正则规则扫描文本，并按章节物理切割文件。
- **文件命名规范**:
    - 切分后的文件名必须包含**序列号**以保持阅读顺序（例如: `001_第一章_重生.txt`, `002_第二章_修炼.txt`）。

## Dependencies (核心依赖)
针对 Epub 处理和文本操作的专用库：

- **`VersOne.Epub:3.2.1`**: .NET 环境下最流行的 Epub 解析库，用于读取 Epub 结构、元数据和内容。
- **`HtmlAgilityPack:1.11.59`**: Epub 内容通常是 HTML 格式。需使用此库去除 HTML 标签，提取纯文本。
- **`System.Text.RegularExpressions`**: (内置库) 用于高频、复杂的章节标题匹配。
- **`System.IO.Abstractions`** (可选): 用于方便测试文件系统操作。

## Config (配置管理)
文本切分的规则通常需要动态调整，应放入配置：

- **关键配置项 (`appsettings.json`)**:
    - `Splitter:ChapterRegex`: `"(^第[0-9一二三四五六七八九十百千]+[章节卷].*)|(^Chapter [0-9]+.*)"` (默认章节匹配正则)
    - `Splitter:MinChapterLength`: `100` (防止将目录或短标题误判为独立章节)
    - `Paths:RawEpubFolder`: 存放原始 Epub 的目录。
    - `Paths:IntermediateTxtFolder`: 存放转换后的大全本 TXT 目录。
    - `Paths:SplitOutputFolder`: 存放分章后的小 TXT 目录。

## Build and run (业务流程)
定义处理管线 (Pipeline)：

1.  **加载**: 使用 `EpubReader` 读取 Epub 文件。
2.  **清洗 (Sanitization)**: 遍历 Epub 的 ReadingOrder。
    - 使用 `HtmlAgilityPack` 移除 `<div>`, `<p>`, `<br>` 等标签。
    - 转换 HTML 实体 (如 `&nbsp;` -> ` `)。
    - 合并所有内容为一个 `StringBuilder` 并保存为 "全本.txt"。
3.  **扫描 (Scanning)**:
    - 逐行读取 "全本.txt"。
    - 使用 `Regex` 匹配章节标题。
4.  **切分 (Splitting)**:
    - 遇到新标题时，将缓冲区内容写入上一个章节文件。
    - 创建新文件，继续写入后续内容。
    - **特殊处理**: 能够识别并保留 "前言" 或 "楔子" (即第一个章节标题前的内容)。

## Logs (日志规范)
- **[INFO]**: 记录转换统计，如 "Epub 解析完成，共包含 120 个 HTML 章节"。
- **[INFO]**: 记录切分结果，如 "切分完成：共生成 540 个 TXT 文件，平均每章 3000 字"。
- **[WARN]**: 如果生成的 TXT 文件过小（< 50 字），警告可能是正则误判。

## AI Coding Rules (AI 编码具体准则)
1.  **正则性能优化**: 章节匹配正则必须使用 `RegexOptions.Compiled`，且需处理多行模式。避免回溯陷阱 (Catastrophic Backtracking)。
2.  **内存管理**: 处理超大文本（如 10MB+ 的小说）时，**禁止**一次性 `File.ReadAllText`。必须使用 `File.ReadLines` 或 `StreamReader` 逐行流式处理，以降低内存占用。
3.  **编码一致性**: 输出的所有 TXT 文件必须强制使用 `UTF-8 (without BOM)` 编码，以确保后续 TTS 模块读取无误。
4.  **文件名清洗**: 生成文件名时，必须移除文件系统非法字符（如 `\ / : * ? " < > |`），替换为下划线 `_`。
5.  **目录结构**: 为每一本书创建一个独立的子文件夹存放其分章 TXT，不要把所有书的章节混在一起。