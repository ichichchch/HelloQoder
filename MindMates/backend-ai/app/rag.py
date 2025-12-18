"""
RAG (Retrieval Augmented Generation) service for psychological knowledge base.
Uses LangChain for orchestration, Zhipu Embedding-v2 for vectors, and hybrid retrieval.

Hybrid retrieval combines:
1. Semantic search (vector similarity via Zhipu API)
2. Keyword matching (for high-precision recall)
"""

from typing import Optional
from functools import lru_cache
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_openai import OpenAIEmbeddings
from app.config import get_settings

settings = get_settings()


# ============================================================================
# Extended Psychology Knowledge Base
# ============================================================================
PSYCHOLOGY_KNOWLEDGE_BASE: list[dict] = [
    # Anxiety
    {
        "topic": "anxiety",
        "content": """焦虑管理技巧：
1. 深呼吸练习：4-7-8呼吸法 - 吸气4秒，屏息7秒，呼气8秒
2. 正念冥想：专注当下，观察自己的想法而不评判
3. 渐进式肌肉放松：从脚趾开始，逐步放松全身肌肉
4. 认知重构：识别和挑战负面自动思维
5. 接地技术：5-4-3-2-1感官练习（5样看到的、4样触摸的、3样听到的、2样闻到的、1样尝到的）
6. 限制咖啡因摄入，保持规律运动
7. 写焦虑日记：记录触发因素和应对策略""",
        "keywords": ["焦虑", "紧张", "担心", "害怕", "恐惧", "不安", "慌", "心慌", "胸闷", "烦躁", "手心出汗", "心跳加速", "考试"]
    },
    # Depression
    {
        "topic": "depression",
        "content": """抑郁情绪应对策略：
1. 行为激活：制定小目标，逐步增加愉悦活动
2. 建立日常规律：保持固定的作息时间，每天同一时间起床
3. 社交连接：与信任的人保持联系，哪怕只是简短交流
4. 运动疗法：每天30分钟中等强度运动，如散步、游泳
5. 自我关怀：对自己保持温和和理解，避免自我批评
6. 阳光暴露：每天至少15分钟户外活动
7. 感恩练习：每天记录3件值得感恩的小事
8. 限制反刍思维：当发现自己反复想同一件事时，用活动打断""",
        "keywords": ["抑郁", "难过", "悲伤", "低落", "消沉", "郁闷", "不开心", "没意思", "无聊", "空虚", "麻木", "绝望", "心情不好", "活着没意义", "哭", "想哭", "流泪", "状态不好", "不舒服", "心里不舒服", "没意义", "活着没什么意义", "状态不太好"]
    },
    # Stress
    {
        "topic": "stress",
        "content": """压力管理方法：
1. 时间管理：使用番茄工作法（25分钟专注+5分钟休息）
2. 任务分解：将大任务分解为小步骤，逐个完成
3. 设定边界：学会说"不"，保护个人时间和精力
4. 自我关怀：安排固定的放松时间，做喜欢的事
5. 问题解决：区分可控和不可控因素，专注于可控部分
6. 寻求支持：与他人分享你的压力，不要独自承担
7. 身体放松：泡热水澡、听音乐、按摩
8. 调整期望：接受"足够好"，不追求完美""",
        "keywords": ["压力", "累", "疲惫", "喘不过气", "忙", "崩溃", "受不了", "扛不住", "太难了", "撑不住", "筋疲力尽", "事情太多", "不知道从何下手"]
    },
    # Sleep Issues
    {
        "topic": "sleep",
        "content": """改善睡眠质量的方法：
1. 睡眠卫生：保持卧室黑暗、安静、凉爽（18-22°C）
2. 规律作息：每天同一时间睡觉和起床，包括周末
3. 睡前放松：睡前1小时避免屏幕，尝试阅读或冥想
4. 限制咖啡因：下午2点后避免咖啡、茶和可乐
5. 运动时机：规律运动但避免睡前3小时内剧烈运动
6. 认知行为疗法：处理睡眠相关焦虑和负面想法
7. 刺激控制：床只用于睡眠，睡不着就起来做放松活动
8. 避免午睡过长：如需午睡，控制在20-30分钟""",
        "keywords": ["失眠", "睡不着", "噩梦", "睡眠", "休息", "入睡困难", "早醒", "多梦", "睡不好", "熬夜", "困"]
    },
    # Relationships
    {
        "topic": "relationship",
        "content": """健康关系建设：
1. 有效沟通：使用"我"陈述表达感受（"我感到..."而非"你总是..."）
2. 主动倾听：全神贯注地听对方说话，不急于反驳或给建议
3. 尊重边界：理解和尊重彼此的个人空间和底线
4. 解决冲突：冷静后再讨论，寻找双赢的解决方案
5. 表达感激：定期表达对伴侣/朋友的感谢和欣赏
6. 质量时间：安排专属的相处时间，放下手机全心投入
7. 接受差异：尊重对方与自己的不同，求同存异
8. 修复关系：出现伤害后主动道歉和弥补""",
        "keywords": ["感情", "恋爱", "分手", "婚姻", "伴侣", "吵架", "冷战", "出轨", "信任", "背叛", "孤独", "被抛弃", "老公", "老婆", "男朋友", "女朋友", "不理解"]
    },
    # Self-esteem
    {
        "topic": "self_esteem",
        "content": """提升自我价值感：
1. 自我接纳：承认自己的不完美，这是人类的共同特点
2. 记录成就：每天写下自己完成的3件事，无论大小
3. 自我对话：用对待好朋友的方式对待自己
4. 设定边界：学会拒绝不合理的要求
5. 挑战负面想法：质疑"我不够好"等自我否定的想法
6. 发展优势：投入时间在自己擅长和喜欢的事情上
7. 减少比较：关注自己的进步，而非与他人比较
8. 寻求反馈：向信任的人询问你的优点""",
        "keywords": ["自卑", "不自信", "没用", "失败", "废物", "差劲", "比不上", "看不起", "嫌弃", "不够好", "配不上", "做不好", "太差了"]
    },
    # Anger Management
    {
        "topic": "anger",
        "content": """愤怒情绪管理：
1. 识别触发点：了解什么情况容易让你生气
2. 暂停技术：感到愤怒时，先离开现场冷静10分钟
3. 深呼吸：用腹式呼吸让身体放松
4. 身体活动：通过运动释放愤怒的能量
5. 认知重构：问自己"这件事一年后还重要吗？"
6. 表达感受：冷静后用"我"陈述表达，而非指责
7. 寻找根源：愤怒常是恐惧或受伤的保护性反应
8. 预防策略：充足睡眠、规律饮食减少易怒""",
        "keywords": ["生气", "愤怒", "烦躁", "暴躁", "发火", "气死了", "恨", "讨厌", "受够了", "忍无可忍", "想打人", "吵起来"]
    },
    # Work-Life Balance
    {
        "topic": "work_life",
        "content": """工作与生活平衡：
1. 明确优先级：区分紧急和重要的事，优先处理重要的
2. 设定工作边界：固定下班时间，避免把工作带回家
3. 学会委托：不必事事亲力亲为，适当分配任务
4. 高效工作：专注时段处理难题，低效时段处理简单任务
5. 休息充电：定期休假，完全脱离工作
6. 培养爱好：工作之外有自己的兴趣和社交
7. 照顾健康：再忙也要保证睡眠、运动和健康饮食
8. 定期反思：评估当前的平衡状态，及时调整""",
        "keywords": ["工作", "加班", "996", "内卷", "裁员", "失业", "找工作", "职场", "领导", "同事", "竞争", "晋升"]
    },
    # Social Anxiety
    {
        "topic": "social_anxiety",
        "content": """社交焦虑应对：
1. 暴露练习：从低焦虑社交场景开始，逐步挑战
2. 认知重构：质疑"别人都在评判我"的想法
3. 关注外部：将注意力从自己转向对话内容和对方
4. 准备话题：提前准备一些可聊的话题减少不安
5. 接受不完美：允许自己在社交中犯错
6. 寻找同类：与理解你的人建立深度友谊
7. 练习小交流：从与陌生人简短交流开始
8. 肯定进步：每次社交后记录做得好的地方""",
        "keywords": ["社恐", "社交", "紧张", "尴尬", "脸红", "不敢", "害怕见人", "不想出门", "人多", "聚会", "演讲"]
    },
    # Grief and Loss
    {
        "topic": "grief",
        "content": """面对丧失与哀伤：
1. 允许悲伤：给自己时间和空间去哀悼
2. 表达情感：通过谈话、写作或艺术表达感受
3. 照顾自己：保持基本的吃饭、睡觉、运动
4. 寻求支持：与理解你的人分享，考虑加入互助小组
5. 保持联系：与逝去的人保持精神上的连接（如写信、纪念）
6. 接受复杂情感：悲伤可能伴随愤怒、内疚等多种情绪
7. 尊重个人节奏：每个人的哀悼过程不同
8. 重建生活：逐渐为生活注入新的意义""",
        "keywords": ["失去", "离世", "去世", "死", "怀念", "想念", "分离", "离别", "告别", "再也", "没有了"]
    },
    # Perfectionism
    {
        "topic": "perfectionism",
        "content": """克服完美主义：
1. 认识代价：完美主义带来的焦虑和拖延
2. 设定"足够好"标准：80%完美就可以交付
3. 限制时间：为任务设定时间限制，到时就停止
4. 拥抱错误：将错误视为学习机会而非失败
5. 区分领域：对重要的事追求卓越，其他事接受一般
6. 挑战非黑即白思维：结果不是"完美"就是"失败"
7. 自我慈悲：像对待好朋友一样对待自己
8. 关注过程：享受做事的过程，而非只看结果""",
        "keywords": ["完美", "强迫", "控制", "必须", "应该", "一定要", "不能出错", "反复检查", "纠结", "犹豫"]
    },
    # Trauma and PTSD
    {
        "topic": "trauma",
        "content": """创伤后的自我照顾：
1. 安全第一：确保当前环境是安全的
2. 接地技术：当闪回发生时，用感官把自己带回当下
3. 规律生活：保持日常作息的稳定性
4. 身体活动：温和的运动帮助释放身体里的创伤记忆
5. 限制触发：暂时减少接触可能触发创伤的事物
6. 表达感受：在安全的环境中讲述经历，或通过写作表达
7. 寻求专业帮助：创伤治疗需要专业心理咨询师的支持
8. 耐心恢复：创伤疗愈需要时间，对自己保持耐心""",
        "keywords": ["创伤", "噩梦", "闪回", "惊恐", "害怕", "阴影", "忘不了", "被伤害", "虐待", "暴力", "侵犯", "小时候", "被打"]
    },
    # Parenting Stress
    {
        "topic": "parenting",
        "content": """育儿压力管理：
1. 自我关怀：照顾好自己才能更好地照顾孩子
2. 降低期望：没有完美的父母，"足够好"就可以
3. 寻求帮助：让伴侣、家人或朋友分担
4. 建立支持网络：与其他父母交流，获得理解和建议
5. 安排独处时间：定期有自己的休息时间
6. 正面关注：关注孩子做得好的地方，而非只纠错
7. 保持耐心：孩子的行为是发展阶段的正常表现
8. 修复关系：对孩子发脾气后主动道歉""",
        "keywords": ["孩子", "育儿", "教育", "父母", "妈妈", "爸爸", "叛逆", "不听话", "学习", "考试", "成绩"]
    },
    # Loneliness
    {
        "topic": "loneliness",
        "content": """应对孤独感：
1. 区分独处与孤独：独处可以是滋养的，关键是选择
2. 主动连接：定期与朋友家人联系，哪怕只是发消息
3. 加入社群：参加兴趣小组、志愿活动或线上社区
4. 培养自我陪伴：学会享受与自己相处的时光
5. 深度交流：与少数人建立深度友谊比广泛社交更重要
6. 帮助他人：志愿服务可以增加社会连接感
7. 接受感受：孤独是人类共同的体验，不必羞耻
8. 专业支持：长期孤独可能需要心理咨询帮助""",
        "keywords": ["孤独", "寂寞", "一个人", "没朋友", "没人理解", "被孤立", "不合群", "格格不入", "被排挤", "边缘", "需要有人听", "没人懂", "真正理解", "没有人理解"]
    },
    # Motivation Issues
    {
        "topic": "motivation",
        "content": """提升动力与行动力：
1. 从微小开始：将任务分解到不可能失败的程度
2. 先行动后动力：不等有动力才行动，行动会带来动力
3. 环境设计：让好习惯更容易，坏习惯更难
4. 奖励自己：完成任务后给自己小奖励
5. 明确"为什么"：连接到更大的人生意义
6. 减少选择：早上最有精力时做最重要的事
7. 责任伙伴：告诉他人你的计划，增加承诺感
8. 接受起伏：动力波动是正常的，关键是持续行动""",
        "keywords": ["没动力", "懒", "拖延", "不想动", "提不起劲", "躺平", "摆烂", "没意义", "迷茫", "不知道想要什么", "什么都不想做", "躺着", "不知道自己想要"]
    }
]


# ============================================================================
# Zhipu Embedding Model (OpenAI-compatible)
# ============================================================================
@lru_cache(maxsize=1)
def get_embedding_model() -> OpenAIEmbeddings:
    """Get the Zhipu embedding model singleton."""
    return OpenAIEmbeddings(
        model=settings.zhipu_embedding_model,
        openai_api_key=settings.zhipu_api_key,
        openai_api_base=settings.zhipu_api_base,
    )


# ============================================================================
# Knowledge Embeddings Cache
# ============================================================================
_knowledge_embeddings: Optional[list[list[float]]] = None


def _get_knowledge_embeddings() -> list[list[float]]:
    """Get or compute embeddings for the knowledge base."""
    global _knowledge_embeddings
    
    if _knowledge_embeddings is None:
        embedding_model = get_embedding_model()
        texts = [item["content"] for item in PSYCHOLOGY_KNOWLEDGE_BASE]
        _knowledge_embeddings = embedding_model.embed_documents(texts)
        print(f"[RAG] Embedded {len(texts)} knowledge documents using Zhipu embedding-2")
    
    return _knowledge_embeddings


def _cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)


# ============================================================================
# Hybrid Retriever
# ============================================================================
class PsychologyKnowledgeRetriever(BaseRetriever):
    """
    Hybrid retriever for psychological counseling knowledge base.
    
    Combines:
    1. Semantic search using Zhipu Embedding-v2
    2. Keyword matching for high-precision recall
    
    This approach significantly improves recall rate compared to
    keyword-only matching.
    """
    
    top_k: int = 5
    similarity_threshold: float = 0.4
    keyword_boost: float = 0.3  # Boost score for keyword matches
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.top_k = settings.rag_top_k
        self.similarity_threshold = settings.rag_similarity_threshold
    
    def _keyword_match_score(self, query: str, keywords: list[str]) -> float:
        """
        Calculate keyword match score.
        
        Returns:
            Score between 0 and 1 based on keyword matches
        """
        query_lower = query.lower()
        matches = sum(1 for kw in keywords if kw in query_lower)
        
        if matches == 0:
            return 0.0
        
        # Normalize by number of keywords, cap at 1.0
        return min(matches / len(keywords) * 2, 1.0)
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> list[Document]:
        """
        Retrieve relevant documents using hybrid search.
        
        Args:
            query: The user's query
            run_manager: Callback manager
            
        Returns:
            List of relevant Document objects
        """
        # Get embedding model and compute query embedding
        embedding_model = get_embedding_model()
        query_embedding = embedding_model.embed_query(query)
        
        # Get knowledge base embeddings
        knowledge_embeddings = _get_knowledge_embeddings()
        
        # Score each document
        scored_docs: list[tuple[float, dict]] = []
        
        for idx, item in enumerate(PSYCHOLOGY_KNOWLEDGE_BASE):
            # Semantic similarity score
            semantic_score = _cosine_similarity(
                query_embedding, 
                knowledge_embeddings[idx]
            )
            
            # Keyword match score
            keyword_score = self._keyword_match_score(query, item["keywords"])
            
            # Hybrid score: combine semantic and keyword scores
            # Keyword matches boost the semantic score
            final_score = semantic_score + (keyword_score * self.keyword_boost)
            
            # Only include if above threshold OR has keyword match
            if final_score >= self.similarity_threshold or keyword_score > 0:
                scored_docs.append((final_score, item))
        
        # Sort by score descending
        scored_docs.sort(key=lambda x: x[0], reverse=True)
        
        # Convert to Document objects
        relevant_docs = []
        for score, item in scored_docs[:self.top_k]:
            doc = Document(
                page_content=item["content"],
                metadata={
                    "topic": item["topic"],
                    "score": score,
                    "keywords": item["keywords"]
                }
            )
            relevant_docs.append(doc)
        
        return relevant_docs


# ============================================================================
# Public API
# ============================================================================
def get_retriever() -> PsychologyKnowledgeRetriever:
    """Get the psychology knowledge retriever instance."""
    return PsychologyKnowledgeRetriever()


async def retrieve_knowledge(query: str) -> list[str]:
    """
    Retrieve relevant psychological knowledge for a query.
    
    Args:
        query: The user's message or query
        
    Returns:
        List of relevant knowledge snippets
    """
    retriever = get_retriever()
    docs = retriever._get_relevant_documents(query)
    
    # Log retrieval results for debugging
    if docs:
        topics = [doc.metadata.get("topic", "unknown") for doc in docs]
        scores = [f"{doc.metadata.get('score', 0):.2f}" for doc in docs]
        print(f"[RAG] Query: '{query[:50]}...' -> Retrieved: {list(zip(topics, scores))}")
    else:
        print(f"[RAG] Query: '{query[:50]}...' -> No relevant documents found")
    
    return [doc.page_content for doc in docs]
