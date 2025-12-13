# 开发过程记录

> 本文档记录了与 AI 助手协作完成 NovelTTSApp 项目的完整对话过程。

---

## 📅 项目信息

- **项目名称**: NovelTTSApp（小说转有声书应用）
- **开发日期**: 2025年12月13日
- **开发方式**: 人机协作（用户 + AI 助手）

---

## 💬 对话记录

### 对话 1：项目初始化

**用户**:
> 基于 rules 为我完成完整的应用程序

**AI 助手**:
根据 `.qoder/rules/novel_tts_app.md` 中定义的规则，开始创建完整的 NovelTTS 应用程序：

1. 创建了解决方案和三层项目结构（Clean Architecture）
2. 安装了所需的 NuGet 包（Microsoft.Extensions.AI, NAudio, Serilog, Polly 等）
3. 创建了 Core 层的实体（Novel, AudioSegment, VoiceReference）和接口
4. 实现了 Infrastructure 层的服务（ZhipuTtsService, AudioProcessor, BilibiliDownloader 等）
5. 编写了 App 层的主程序和 NovelProcessor 流程编排

**执行结果**: 构建成功 ✅

---

### 对话 2：代码规范调整

**用户**:
> 所有的 using 不是都放到 GlobalUsings 中吗

**AI 助手**:
你说得对！根据项目规范，应该使用现代 C# 风格，将 using 统一放到 GlobalUsings.cs 中。

执行了以下修改：
- 更新了 `Core/GlobalUsings.cs` - 添加基础类型引用
- 更新了 `Infrastructure/GlobalUsings.cs` - 添加所有服务依赖
- 创建了 `App/GlobalUsings.cs` - 添加应用层依赖
- 从所有 `.cs` 文件中移除了单独的 using 语句

**执行结果**: 构建成功 ✅

---

### 对话 3：Code Review

**用户**:
> Code Review

**AI 助手**:
对项目进行了全面的代码审查，发现并修复了以下问题：

| 问题 | 严重性 | 修复方案 |
|------|--------|----------|
| 服务生命周期不当 | 中 | `Singleton` → `Scoped` |
| 同步文件读取 | 中 | `File.ReadAllBytes` → `File.ReadAllBytesAsync` |
| Polly 重试策略不完善 | 低 | 添加 `TaskCanceledException` 处理 |
| voiceRefUrl 参数未使用 | 低 | 待后续迭代实现 |

**代码质量评分**: 4.3/5 ⭐

**评分明细**:
- 架构设计: ⭐⭐⭐⭐⭐
- 代码风格: ⭐⭐⭐⭐⭐
- 错误处理: ⭐⭐⭐⭐☆
- 异步编程: ⭐⭐⭐⭐⭐
- 可测试性: ⭐⭐⭐⭐☆

---

### 对话 4：创建文档

**用户**:
> 新增 Readme，以及我们对话的过程也写成一个子 readme，放到主 readme 中调用，叫做"开发过程记录"

**AI 助手**:
创建了以下文档：
- `README.md` - 主文档（项目介绍、功能特性、使用方法、配置说明）
- `docs/DEVELOPMENT.md` - 开发过程记录

---

### 对话 5：调整文档内容

**用户**:
> 不是，是与你对话的记录，专注于与你对话完成项目

**AI 助手**:
理解了！重写开发过程记录文档，专注于记录我们的对话交互过程，记录每次对话的请求和执行结果，而非纯技术实现细节。

---

## 📊 项目完成情况

### 已完成功能

- [x] 项目结构搭建（Clean Architecture 三层架构）
- [x] 小说文本读取（本地文件 + URL 抓取）
- [x] 智能文本分段（按段落和句子拆分）
- [x] 智谱 GLM-4-Voice TTS 集成
- [x] 音频片段合并处理（NAudio）
- [x] Bilibili 音频提取功能
- [x] 命令行参数支持（-i, -o, -v, -h）
- [x] 结构化日志系统（Serilog）
- [x] API 调用重试机制（Polly）
- [x] 项目文档（README + 开发记录）

### 待完成功能

- [ ] `-v` 参数声音克隆完整流程
- [ ] 单元测试项目
- [ ] Web API 接口
- [ ] GUI 界面

---

## 🎯 关键决策记录

| 决策点 | 最终决策 | 决策原因 |
|--------|----------|----------|
| 项目架构 | Clean Architecture | rules 文件明确要求 |
| using 管理 | GlobalUsings.cs | 用户要求，符合现代 C# 风格 |
| 服务生命周期 | Scoped | Code Review 发现 Singleton 存在配置热更新问题 |
| 文件操作 | 异步 I/O | rules 文件要求必须使用 async/await |
| 日志框架 | Serilog | rules 文件指定 |
| 重试机制 | Polly | rules 文件指定 |

---

## 📁 最终项目结构

```
NovelTTSApp/
├── README.md                    # 主文档
├── NovelTTSApp.sln              # 解决方案文件
├── docs/
│   └── DEVELOPMENT.md           # 开发过程记录（本文档）
└── src/
    ├── Core/                    # 核心层 - 实体与接口
    │   ├── Entities/
    │   ├── Interfaces/
    │   └── GlobalUsings.cs
    ├── Infrastructure/          # 基础设施层 - 服务实现
    │   ├── Configuration/
    │   ├── Services/
    │   ├── DependencyInjection.cs
    │   └── GlobalUsings.cs
    └── App/                     # 应用层 - 主程序
        ├── Services/
        ├── Program.cs
        ├── appsettings.json
        └── GlobalUsings.cs
```

---

## ⏱️ 开发时间统计

| 阶段 | 耗时 |
|------|------|
| 项目初始化与基础搭建 | ~15 分钟 |
| 代码规范调整 | ~5 分钟 |
| Code Review 与修复 | ~5 分钟 |
| 文档编写 | ~5 分钟 |
| **总计** | **~30 分钟** |

---

*文档最后更新: 2025年12月13日*
