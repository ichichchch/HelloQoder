"""
RAG 召回率测试脚本
==================

测试指标:
- Recall@K: 在返回的 K 个结果中，是否包含期望的主题
- MRR (Mean Reciprocal Rank): 期望主题在结果中的平均排名倒数
- Hit Rate: 成功召回的测试用例占比

运行方式:
    cd backend-ai
    python -m tests.test_rag_recall
"""

import sys
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.rag import retrieve_knowledge, get_retriever, PSYCHOLOGY_KNOWLEDGE_BASE


@dataclass
class TestCase:
    """单个测试用例"""
    query: str                      # 用户输入
    expected_topics: list[str]      # 期望召回的主题
    description: str = ""           # 测试说明


# ============================================================================
# 测试用例集
# ============================================================================
TEST_CASES: list[TestCase] = [
    # === 焦虑相关 ===
    TestCase(
        query="我最近总是很紧张，心跳加速",
        expected_topics=["anxiety"],
        description="直接表达焦虑症状"
    ),
    TestCase(
        query="我总是担心事情会变糟糕",
        expected_topics=["anxiety"],
        description="焦虑的认知表现"
    ),
    TestCase(
        query="每次考试前我都会手心出汗，脑子一片空白",
        expected_topics=["anxiety", "social_anxiety"],
        description="考试焦虑场景"
    ),
    TestCase(
        query="我害怕坐飞机",
        expected_topics=["anxiety"],
        description="特定恐惧"
    ),
    
    # === 抑郁相关 ===
    TestCase(
        query="我感觉什么都没意思，每天都很空虚",
        expected_topics=["depression", "motivation"],
        description="抑郁核心症状"
    ),
    TestCase(
        query="心情不好，不想和任何人说话",
        expected_topics=["depression", "loneliness"],
        description="抑郁伴随社交退缩"
    ),
    TestCase(
        query="我觉得活着没什么意义",
        expected_topics=["depression"],
        description="存在性抑郁"
    ),
    TestCase(
        query="最近总是哭，控制不住",
        expected_topics=["depression"],
        description="情绪失控"
    ),
    
    # === 压力相关 ===
    TestCase(
        query="工作太多了，感觉喘不过气",
        expected_topics=["stress", "work_life"],
        description="工作压力"
    ),
    TestCase(
        query="每天加班到很晚，身心俱疲",
        expected_topics=["stress", "work_life"],
        description="996工作压力"
    ),
    TestCase(
        query="事情太多了，不知道从何下手",
        expected_topics=["stress", "motivation"],
        description="任务过载"
    ),
    
    # === 睡眠问题 ===
    TestCase(
        query="晚上翻来覆去睡不着",
        expected_topics=["sleep"],
        description="入睡困难"
    ),
    TestCase(
        query="每天凌晨3点就醒了，再也睡不着",
        expected_topics=["sleep"],
        description="早醒"
    ),
    TestCase(
        query="最近老做噩梦",
        expected_topics=["sleep", "trauma"],
        description="噩梦"
    ),
    
    # === 人际关系 ===
    TestCase(
        query="和男朋友吵架了，不知道怎么办",
        expected_topics=["relationship"],
        description="恋爱冲突"
    ),
    TestCase(
        query="感觉老公不理解我",
        expected_topics=["relationship"],
        description="婚姻沟通问题"
    ),
    TestCase(
        query="分手了，很难过",
        expected_topics=["relationship", "grief"],
        description="失恋"
    ),
    
    # === 自尊问题 ===
    TestCase(
        query="我觉得自己什么都做不好",
        expected_topics=["self_esteem"],
        description="自我否定"
    ),
    TestCase(
        query="和别人比起来，我太差了",
        expected_topics=["self_esteem"],
        description="社会比较"
    ),
    TestCase(
        query="我是个废物",
        expected_topics=["self_esteem", "depression"],
        description="极度自我贬低"
    ),
    
    # === 愤怒管理 ===
    TestCase(
        query="我好生气，想摔东西",
        expected_topics=["anger"],
        description="愤怒表达"
    ),
    TestCase(
        query="每次和父母说话都会吵起来",
        expected_topics=["anger", "relationship"],
        description="家庭冲突"
    ),
    
    # === 社交焦虑 ===
    TestCase(
        query="我不敢在人多的地方说话",
        expected_topics=["social_anxiety"],
        description="公开场合焦虑"
    ),
    TestCase(
        query="社恐，不想参加聚会",
        expected_topics=["social_anxiety"],
        description="社交回避"
    ),
    TestCase(
        query="当众演讲让我非常紧张",
        expected_topics=["social_anxiety", "anxiety"],
        description="演讲焦虑"
    ),
    
    # === 孤独感 ===
    TestCase(
        query="感觉没有人真正理解我",
        expected_topics=["loneliness"],
        description="情感孤独"
    ),
    TestCase(
        query="一个人待着，没有朋友",
        expected_topics=["loneliness"],
        description="社交孤立"
    ),
    
    # === 动力缺失 ===
    TestCase(
        query="什么都不想做，就想躺着",
        expected_topics=["motivation", "depression"],
        description="动力缺失"
    ),
    TestCase(
        query="一直拖延，事情越堆越多",
        expected_topics=["motivation", "stress"],
        description="拖延症"
    ),
    TestCase(
        query="不知道自己想要什么",
        expected_topics=["motivation"],
        description="人生迷茫"
    ),
    
    # === 工作问题 ===
    TestCase(
        query="被裁员了，很焦虑",
        expected_topics=["work_life", "anxiety"],
        description="失业焦虑"
    ),
    TestCase(
        query="领导总是针对我",
        expected_topics=["work_life", "stress"],
        description="职场人际"
    ),
    
    # === 丧失与哀伤 ===
    TestCase(
        query="爷爷去世了，我很难过",
        expected_topics=["grief"],
        description="亲人离世"
    ),
    TestCase(
        query="很想念去世的妈妈",
        expected_topics=["grief"],
        description="思念逝者"
    ),
    
    # === 创伤 ===
    TestCase(
        query="小时候被打的画面总是出现在脑海里",
        expected_topics=["trauma"],
        description="童年创伤闪回"
    ),
    TestCase(
        query="那件事过去很久了，但我还是忘不了",
        expected_topics=["trauma", "grief"],
        description="创伤记忆"
    ),
    
    # === 育儿 ===
    TestCase(
        query="孩子不听话，我都快崩溃了",
        expected_topics=["parenting", "stress"],
        description="育儿压力"
    ),
    TestCase(
        query="孩子成绩不好，我很着急",
        expected_topics=["parenting"],
        description="学业焦虑"
    ),
    
    # === 完美主义 ===
    TestCase(
        query="我总是反复检查，怕出错",
        expected_topics=["perfectionism", "anxiety"],
        description="完美主义检查行为"
    ),
    TestCase(
        query="做事必须做到最好，否则就是失败",
        expected_topics=["perfectionism"],
        description="完美主义思维"
    ),
    
    # === 边缘/模糊表达 ===
    TestCase(
        query="最近状态不太好",
        expected_topics=["depression", "stress"],
        description="模糊表达-测试泛化能力"
    ),
    TestCase(
        query="心里不舒服",
        expected_topics=["depression", "anxiety"],
        description="非特定情绪困扰"
    ),
    TestCase(
        query="我需要有人听我说说话",
        expected_topics=["loneliness"],
        description="寻求倾听"
    ),
]


# ============================================================================
# 评估逻辑
# ============================================================================
@dataclass
class EvalResult:
    """单个测试用例的评估结果"""
    query: str
    expected_topics: list[str]
    retrieved_topics: list[str]
    hit: bool                       # 是否至少命中一个期望主题
    recall: float                   # 期望主题的召回率
    reciprocal_rank: float          # 第一个命中的倒数排名
    scores: list[float]             # 各文档的相似度分数


def evaluate_single(query: str, expected_topics: list[str], docs: list) -> EvalResult:
    """评估单个测试用例"""
    retrieved_topics = [doc.metadata.get("topic", "") for doc in docs]
    scores = [doc.metadata.get("score", 0) for doc in docs]
    
    # 计算召回率
    hits = [t for t in expected_topics if t in retrieved_topics]
    recall = len(hits) / len(expected_topics) if expected_topics else 0
    
    # 计算 MRR
    reciprocal_rank = 0.0
    for i, topic in enumerate(retrieved_topics):
        if topic in expected_topics:
            reciprocal_rank = 1.0 / (i + 1)
            break
    
    return EvalResult(
        query=query,
        expected_topics=expected_topics,
        retrieved_topics=retrieved_topics,
        hit=len(hits) > 0,
        recall=recall,
        reciprocal_rank=reciprocal_rank,
        scores=scores
    )


async def run_evaluation() -> dict:
    """运行完整评估"""
    print("=" * 70)
    print("RAG 召回率测试报告")
    print("=" * 70)
    print(f"\n知识库主题数: {len(PSYCHOLOGY_KNOWLEDGE_BASE)}")
    print(f"测试用例数: {len(TEST_CASES)}\n")
    
    retriever = get_retriever()
    results: list[EvalResult] = []
    
    print("-" * 70)
    print(f"{'序号':<4} {'查询':<30} {'期望':<20} {'召回':<20} {'命中':<6}")
    print("-" * 70)
    
    for i, tc in enumerate(TEST_CASES, 1):
        docs = retriever._get_relevant_documents(tc.query)
        result = evaluate_single(tc.query, tc.expected_topics, docs)
        results.append(result)
        
        # 格式化输出
        query_display = tc.query[:28] + ".." if len(tc.query) > 30 else tc.query
        expected_display = ",".join(tc.expected_topics)[:18]
        retrieved_display = ",".join(result.retrieved_topics[:3])[:18]
        hit_mark = "✓" if result.hit else "✗"
        
        print(f"{i:<4} {query_display:<30} {expected_display:<20} {retrieved_display:<20} {hit_mark:<6}")
    
    # 计算总体指标
    total = len(results)
    hit_count = sum(1 for r in results if r.hit)
    avg_recall = sum(r.recall for r in results) / total
    avg_mrr = sum(r.reciprocal_rank for r in results) / total
    
    print("-" * 70)
    print("\n" + "=" * 70)
    print("评估指标汇总")
    print("=" * 70)
    
    metrics = {
        "total_cases": total,
        "hit_count": hit_count,
        "hit_rate": hit_count / total,
        "avg_recall": avg_recall,
        "mrr": avg_mrr,
    }
    
    print(f"""
    测试用例总数:    {total}
    命中用例数:      {hit_count}
    
    ┌─────────────────────────────────────┐
    │  Hit Rate (命中率):   {metrics['hit_rate']:.1%}          │
    │  Avg Recall (召回率): {metrics['avg_recall']:.1%}          │
    │  MRR (平均倒数排名):  {metrics['mrr']:.3f}           │
    └─────────────────────────────────────┘
    """)
    
    # 失败用例分析
    failed = [r for r in results if not r.hit]
    if failed:
        print("=" * 70)
        print(f"未命中用例分析 ({len(failed)} 个)")
        print("=" * 70)
        for r in failed:
            print(f"\n  查询: {r.query}")
            print(f"  期望: {r.expected_topics}")
            print(f"  召回: {r.retrieved_topics}")
            if r.scores:
                print(f"  分数: {[f'{s:.3f}' for s in r.scores]}")
    
    return metrics


def print_knowledge_base_summary():
    """打印知识库摘要"""
    print("\n" + "=" * 70)
    print("知识库摘要")
    print("=" * 70)
    for item in PSYCHOLOGY_KNOWLEDGE_BASE:
        keywords_str = ", ".join(item["keywords"][:5])
        if len(item["keywords"]) > 5:
            keywords_str += f" (+{len(item['keywords'])-5})"
        print(f"  [{item['topic']:<18}] {keywords_str}")


if __name__ == "__main__":
    print_knowledge_base_summary()
    print()
    
    # 运行评估
    metrics = asyncio.run(run_evaluation())
    
    # 输出建议
    print("\n" + "=" * 70)
    print("优化建议")
    print("=" * 70)
    
    if metrics["hit_rate"] < 0.8:
        print("  ⚠ Hit Rate < 80%: 考虑增加更多关键词或降低相似度阈值")
    if metrics["avg_recall"] < 0.6:
        print("  ⚠ Recall < 60%: 考虑增加 top_k 或扩展知识库覆盖范围")
    if metrics["mrr"] < 0.7:
        print("  ⚠ MRR < 0.7: 最相关的结果排名不够靠前，检查嵌入模型质量")
    
    if metrics["hit_rate"] >= 0.9 and metrics["avg_recall"] >= 0.7:
        print("  ✓ 召回率表现良好!")
    
    print()
