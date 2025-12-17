"""
RAG (Retrieval Augmented Generation) service for psychological knowledge base.
Uses LangChain for orchestration and Milvus for vector storage.
"""

from typing import Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun


class PsychologyKnowledgeRetriever(BaseRetriever):
    """
    Custom retriever for psychological counseling knowledge base.
    
    This retriever is designed to fetch relevant psychological
    counseling techniques, coping strategies, and mental health
    information based on user queries.
    """
    
    # Knowledge base (in production, this would be from Milvus)
    knowledge_base: list[dict] = []
    top_k: int = 3
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Initialize with some basic psychological knowledge
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> list[dict]:
        """Load the psychological knowledge base."""
        # In production, this would connect to Milvus
        # For now, using a static knowledge base
        return [
            {
                "topic": "anxiety",
                "content": """焦虑管理技巧：
1. 深呼吸练习：4-7-8呼吸法 - 吸气4秒，屏息7秒，呼气8秒
2. 正念冥想：专注当下，观察自己的想法而不评判
3. 渐进式肌肉放松：从脚趾开始，逐步放松全身肌肉
4. 认知重构：识别和挑战负面自动思维
5. 接地技术：5-4-3-2-1感官练习""",
                "keywords": ["焦虑", "紧张", "担心", "害怕", "恐惧"]
            },
            {
                "topic": "depression",
                "content": """抑郁情绪应对策略：
1. 行为激活：制定小目标，逐步增加活动
2. 建立日常规律：保持固定的作息时间
3. 社交连接：与信任的人保持联系
4. 运动：每天30分钟中等强度运动
5. 自我关怀：对自己保持温和和理解""",
                "keywords": ["抑郁", "难过", "悲伤", "低落", "消沉"]
            },
            {
                "topic": "stress",
                "content": """压力管理方法：
1. 时间管理：使用番茄工作法
2. 设定边界：学会说"不"
3. 自我关怀：安排放松时间
4. 问题解决：将大问题分解为小步骤
5. 寻求支持：与他人分享你的压力""",
                "keywords": ["压力", "累", "疲惫", "喘不过气", "忙"]
            },
            {
                "topic": "sleep",
                "content": """改善睡眠质量的方法：
1. 睡眠卫生：保持卧室黑暗、安静、凉爽
2. 规律作息：每天同一时间睡觉和起床
3. 睡前放松：避免屏幕，尝试阅读或冥想
4. 限制咖啡因：下午后避免咖啡和茶
5. 认知行为疗法：处理睡眠相关焦虑""",
                "keywords": ["失眠", "睡不着", "噩梦", "睡眠", "休息"]
            },
            {
                "topic": "relationship",
                "content": """健康关系建设：
1. 有效沟通：使用"我"陈述表达感受
2. 主动倾听：全神贯注地听对方说话
3. 尊重边界：理解和尊重彼此的界限
4. 解决冲突：寻找双赢的解决方案
5. 表达感激：定期表达对伴侣的感谢""",
                "keywords": ["感情", "恋爱", "分手", "婚姻", "伴侣"]
            }
        ]
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None
    ) -> list[Document]:
        """
        Retrieve relevant documents based on query.
        
        Args:
            query: The user's query
            run_manager: Callback manager
            
        Returns:
            List of relevant Document objects
        """
        relevant_docs = []
        query_lower = query.lower()
        
        for item in self.knowledge_base:
            # Check if any keyword matches
            for keyword in item["keywords"]:
                if keyword in query_lower:
                    doc = Document(
                        page_content=item["content"],
                        metadata={"topic": item["topic"]}
                    )
                    relevant_docs.append(doc)
                    break
        
        return relevant_docs[:self.top_k]


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
    return [doc.page_content for doc in docs]
