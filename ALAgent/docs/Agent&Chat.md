# ALAgent 开发对话记录

> 本文档记录了使用 AI Agent 开发 ALAgent 项目的完整流程，详细展示了如何通过交互式调试解决 RAG 服务的 Web Crawl 功能问题，包含完整的问题定位、解决方案和经验总结。

---

## 📅 开发日期

**2025-12-30**

---

## 🎯 目标

解决 RAG 服务的 `/api/load/web` 端点在爬取网页并生成嵌入向量时的错误，优化 API 配置和环境变量管理。

## 🏗️ 系统架构

```
VS Code Extension
    ↓ (Webview Messages)
Extension Host (TypeScript)
    ↓ (HTTP API)
.NET Agent Service
    ↓ (HTTP API)
Python RAG Service
    ↓ (Milvus gRPC)
Milvus Vector Database
```

---

## 问题排查过程

### 1. 初始问题：401 API Key 错误

**终端错误日志：**
```
2025-12-30 18:24:06,736 - app.main - ERROR - Web crawl error: Error code: 401 - 
{'error': {'message': 'Incorrect API key provided...', 'code': 'invalid_api_key'}}
```

**用户反馈：** "不是 API Key 的问题，API Key 可以正常使用"

**分析：** 检查 `vector_store.py` 和 `config.py`，发现嵌入服务初始化代码。

---

### 2. 第一次修复尝试：参数名更新

**发现问题：** `langchain-openai` 新版本的参数名已变更：
- `openai_api_key` → `api_key`
- `openai_api_base` → `base_url`

**修复代码：**
```python
# 修复前
self._embeddings = OpenAIEmbeddings(
    model=self.settings.text_embedding_model,
    openai_api_key=self.settings.dashscope_api_key,
    openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# 修复后
self._embeddings = OpenAIEmbeddings(
    model=self.settings.text_embedding_model,
    api_key=self.settings.dashscope_api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)
```

**结果：** 问题仍然存在 ❌

---

### 3. 添加调试日志

**修改：** 在 `_ensure_embeddings()` 方法中添加日志，打印实际使用的 API Key 前缀：

```python
logger.info(f"Using DashScope embedding with key: {self.settings.dashscope_api_key[:8]}...")
```

**发现：** 日志显示 `sk-ecb82...`，但 `.env` 中配置的是 `sk-4058a...`！

---

### 4. 发现系统环境变量覆盖

**根因：** 系统环境变量中存在另一个 `DASHSCOPE_API_KEY`，其优先级高于 `.env` 文件。

**解决方案：**
1. 打开系统环境变量设置（`Win + R` → `sysdm.cpl`）
2. 删除用户/系统变量中的 `DASHSCOPE_API_KEY`
3. **关闭终端并重新打开**（清除已加载的环境变量）
4. 重启服务

**经验教训：** 
> ⚠️ 修改环境变量后，必须重新打开终端窗口才能生效！

---

### 5. 新错误：400 InvalidParameter

**终端错误日志：**
```
2025-12-30 18:58:41 - ERROR - Web crawl error: Error code: 400 - 
{'error': {'message': 'contents is neither str nor list of str.: input.contents'}}
```

**分析：** DashScope 的 OpenAI 兼容模式对嵌入 API 的请求格式有差异，`OpenAIEmbeddings` 不完全兼容。

---

### 6. 切换到专用 DashScopeEmbeddings

**解决方案：** 使用 LangChain 提供的专门 DashScope 嵌入客户端。

**安装依赖：**
```bash
uv add dashscope
```

**代码修改：**
```python
# 导入
from langchain_community.embeddings import DashScopeEmbeddings

# 初始化
if self.settings.dashscope_api_key:
    self._embeddings = DashScopeEmbeddings(
        model=self.settings.text_embedding_model,
        dashscope_api_key=self.settings.dashscope_api_key,
    )
```

---

### 7. 新错误：Milvus 向量维度不匹配

**终端错误日志：**
```
2025-12-30 19:03:23 - ERROR - Web crawl error: <MilvusException: 
(code=65535, message=the length(4096) of float data should divide the dim(1536))>
```

**分析：** 
- Milvus 集合之前用 1536 维创建（OpenAI 默认）
- DashScope `text-embedding-v4` 返回 1024 维向量
- 4096 bytes / 4 bytes per float = 1024 维

**解决方案：** 删除旧集合，让系统用正确维度重新创建：

```bash
uv run python -c "
from pymilvus import connections, utility
connections.connect('default', host='localhost', port='19530')
utility.drop_collection('global_documents')
print('Done')
"
```

---

### 8. 最后的网络问题：SSL 错误

**终端错误日志：**
```
2025-12-30 19:26:36 - ERROR - HTTPSConnectionPool(host='dashscope.aliyuncs.com', port=443): 
Max retries exceeded... SSLError(SSLEOFError(8, '[SSL: UNEXPECTED_EOF_WHILE_READING]'))
```

**可能原因：**
- 网络代理干扰 SSL 连接
- VPN 或防火墙拦截
- 临时网络波动

**排查步骤：**
```powershell
# 检查代理设置
$env:HTTP_PROXY
$env:HTTPS_PROXY

# 临时禁用代理
$env:HTTP_PROXY = $null
$env:HTTPS_PROXY = $null
```

### 9. 代码实现优化

**优化向量存储初始化：**
```python
# 改进的向量存储初始化逻辑
async def _ensure_embeddings(self):
    """Lazy initialization of embedding model with proper error handling."""
    if self._embeddings is None:
        try:
            # 优先使用 DashScope
            if self.settings.dashscope_api_key:
                logger.info(f"Using DashScope embedding with key: {self.settings.dashscope_api_key[:8]}...")
                self._embeddings = DashScopeEmbeddings(
                    model=self.settings.text_embedding_model,
                    dashscope_api_key=self.settings.dashscope_api_key,
                )
            # 回退到 OpenAI
            elif self.settings.openai_api_key:
                logger.info(f"Using OpenAI embedding with key: {self.settings.openai_api_key[:8]}...")
                self._embeddings = OpenAIEmbeddings(
                    model=self.settings.text_embedding_model,
                    api_key=self.settings.openai_api_key,
                )
            else:
                raise ValueError(
                    "No embedding API key configured. Set DASHSCOPE_API_KEY or OPENAI_API_KEY in .env"
                )
        except Exception as e:
            logger.error(f"Failed to initialize embeddings: {e}")
            raise
    return self._embeddings
```

**添加配置验证：**
```python
# 在 config.py 中添加配置验证
@validator('dashscope_api_key', 'openai_api_key', pre=True)
@classmethod
def validate_api_key(cls, v):
    if v and not v.startswith(('sk-', 'sk-ecb8', 'sk-4058')):
        raise ValueError('Invalid API key format')
    return v
```

---

## 📝 修改的文件清单

| 文件 | 修改内容 | 影响 |
|------|----------|------|
| `backend-rag/app/vector_store.py` | 1. 修复 OpenAIEmbeddings 参数名<br>2. 添加调试日志<br>3. 切换到 DashScopeEmbeddings<br>4. 优化错误处理 | 解决 API 兼容性问题 |
| `backend-rag/pyproject.toml` | 添加 `dashscope` 依赖 | 支持专用 DashScope 客户端 |
| `backend-rag/.env.example` | 添加环境变量说明 | 改善配置文档 |
| `backend-rag/app/config.py` | 添加配置验证 | 提高配置安全性 |

---

## 🚀 系统优化建议

### 1. 性能优化
- **连接池管理**: 为 Milvus 连接添加连接池
- **缓存策略**: 实现嵌入向量缓存减少重复计算
- **异步处理**: 优化 Web 爬虫的异步并发

### 2. 安全增强
- **API 限流**: 添加请求频率限制
- **认证机制**: 实现更严格的 API 认证
- **输入验证**: 增强 URL 和参数验证

### 3. 监控告警
- **健康检查**: 增强健康检查端点
- **指标收集**: 添加性能指标监控
- **日志分析**: 实现结构化日志输出

## 💡 关键经验总结

### 1. 环境变量优先级
系统环境变量 > 用户环境变量 > `.env` 文件

修改 `.env` 后如果不生效，检查是否有系统环境变量覆盖。

### 2. 终端会话与环境变量
修改环境变量后，必须**关闭并重新打开终端**，新的环境变量才能生效。`--reload` 只监听代码变更，不检测环境变量变化。

### 3. LangChain 版本兼容性
`langchain-openai` 新版本参数名变更：
- `openai_api_key` → `api_key`
- `openai_api_base` → `base_url`

### 4. DashScope 最佳实践
使用 DashScope 时，优先使用 `DashScopeEmbeddings` 而非 OpenAI 兼容模式，避免请求格式不兼容问题。

### 5. 向量数据库维度匹配
更换嵌入模型后，需要删除旧的 Milvus 集合，因为不同模型的向量维度可能不同：
- OpenAI `text-embedding-3-small`: 1536 维
- DashScope `text-embedding-v4`: 1024 维

---

## 🔧 常用调试命令

```bash
# 启动 RAG 服务
cd backend-rag
uv run fastapi dev app/main.py --port 8228

# 查看 Milvus 集合
uv run python -c "from pymilvus import connections, utility; connections.connect('default', host='localhost', port='19530'); print(utility.list_collections())"

# 删除 Milvus 集合
uv run python -c "from pymilvus import connections, utility; connections.connect('default', host='localhost', port='19530'); utility.drop_collection('collection_name')"

# 检查环境变量
$env:DASHSCOPE_API_KEY

# 测试 API 端点
curl -X POST http://localhost:8000/api/load/web \
  -H "Content-Type: application/json" \
  -d '{"urls":["https://example.com"]}'
```

---

## 📊 问题解决流程图

```
401 API Key Error
       │
       ▼
修复参数名 (api_key, base_url)
       │
       ▼
仍然 401 → 添加调试日志
       │
       ▼
发现 Key 不一致 → 系统环境变量覆盖
       │
       ▼
删除环境变量 + 重开终端
       │
       ▼
400 InvalidParameter → 切换到 DashScopeEmbeddings
       │
       ▼
Milvus 维度不匹配 → 删除旧集合
       │
       ▼
SSL 网络错误 → 检查代理/VPN
       │
       ▼
问题解决 ← 系统正常运行
```

## 🎯 后续改进方向

### 1. 功能增强
- **多模型支持**: 支持更多嵌入模型和 LLM 服务
- **批量处理**: 优化大批量数据处理性能
- **实时同步**: 实现代码库变更的实时索引

### 2. 运维优化
- **容器化部署**: 提供 Docker Compose 部署方案
- **监控告警**: 集成 Prometheus + Grafana 监控
- **日志中心**: 集成 ELK 日志分析系统

### 3. 用户体验
- **Web 管理界面**: 提供可视化的 RAG 管理界面
- **进度反馈**: 增强长时间操作的进度显示
- **错误恢复**: 实现自动重试和错误恢复机制

---

---

## 总结

### 完成的工作

1. ✅ 设计三层架构 (VS Code Extension / .NET Agent / Python RAG)
2. ✅ 实现 Microsoft Agent Framework 集成
3. ✅ 开发 LangChain + Milvus RAG 服务
4. ✅ 解决 DashScope 嵌入模型集成问题
5. ✅ 修复 Milvus 向量维度不匹配问题
6. ✅ 优化环境变量管理
7. ✅ 编写项目文档

### 技术要点

- **Agent 框架**: 基于 Microsoft Agent Framework 构建
- **RAG 检索**: LangChain + Milvus 向量数据库
- **嵌入模型**: 支持 DashScope 和 OpenAI 双模式
- **知识图谱**: LightRAG 增强检索
- **工具调用**: 文件系统 + 代码分析工具

---

*文档生成时间：2025-12-30*

## 📞 技术支持

如遇到类似问题，建议按以下顺序排查：
1. 检查环境变量配置
2. 验证 API 密钥有效性
3. 确认网络连接正常
4. 查看详细错误日志
5. 参考本文档的解决方案
