"""
Crisis detection module for mental health safety.
Detects potential crisis situations and provides appropriate resources.
"""

import re
from typing import NamedTuple


class CrisisResult(NamedTuple):
    is_crisis: bool
    intent: str | None
    crisis_response: str | None


# Crisis-related keywords and phrases (Chinese)
CRISIS_KEYWORDS = [
    # Suicidal ideation
    "自杀", "不想活", "结束生命", "活不下去", "死掉", "想死", 
    "了结", "解脱", "跳楼", "割腕", "服药自杀", "上吊",
    # Self-harm
    "自残", "伤害自己", "割自己", "打自己",
    # Severe depression indicators
    "没有希望", "绝望", "活着没意义", "世界没有我会更好",
    "没人会想念我", "没人在乎我",
    # Violence
    "杀人", "伤害他人", "报复",
]

# Patterns for crisis detection
CRISIS_PATTERNS = [
    r"想.*死",
    r"不想.*活",
    r"活.*不下去",
    r"没有.*希望",
    r"结束.*一切",
]

# Crisis resources in Chinese
CRISIS_RESOURCES = """
我非常担心你现在的状态。请记住，你的生命很宝贵，有人愿意帮助你。

**立即寻求帮助：**
- 全国心理援助热线：400-161-9995（24小时）
- 北京心理危机研究与干预中心：010-82951332
- 生命热线：400-821-1215
- 希望24热线：400-161-9995

请现在就拨打这些电话，和专业的人谈谈。我会一直在这里陪伴你。
"""


def detect_crisis(message: str) -> CrisisResult:
    """
    Detect if a message indicates a crisis situation.
    
    Args:
        message: The user's message to analyze
        
    Returns:
        CrisisResult with detection results
    """
    message_lower = message.lower()
    
    # Check for direct keyword matches
    for keyword in CRISIS_KEYWORDS:
        if keyword in message_lower:
            return CrisisResult(
                is_crisis=True,
                intent="crisis",
                crisis_response=CRISIS_RESOURCES
            )
    
    # Check for pattern matches
    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, message_lower):
            return CrisisResult(
                is_crisis=True,
                intent="crisis",
                crisis_response=CRISIS_RESOURCES
            )
    
    # Classify other intents
    intent = classify_intent(message_lower)
    
    return CrisisResult(
        is_crisis=False,
        intent=intent,
        crisis_response=None
    )


def classify_intent(message: str) -> str | None:
    """
    Classify the general intent of a message.
    
    Args:
        message: The user's message to classify
        
    Returns:
        Intent classification string or None
    """
    # Emotional states
    if any(word in message for word in ["焦虑", "紧张", "担心", "害怕"]):
        return "anxiety"
    if any(word in message for word in ["难过", "悲伤", "哭", "伤心", "抑郁", "低落"]):
        return "sadness"
    if any(word in message for word in ["生气", "愤怒", "烦躁", "恼火"]):
        return "anger"
    if any(word in message for word in ["孤独", "寂寞", "没人理解"]):
        return "loneliness"
    if any(word in message for word in ["压力", "累", "疲惫", "喘不过气"]):
        return "stress"
    if any(word in message for word in ["失眠", "睡不着", "噩梦"]):
        return "sleep_issues"
    if any(word in message for word in ["工作", "职场", "同事", "领导", "辞职"]):
        return "work"
    if any(word in message for word in ["感情", "恋爱", "分手", "离婚", "婚姻"]):
        return "relationship"
    if any(word in message for word in ["家人", "父母", "孩子", "家庭"]):
        return "family"
    
    return None
