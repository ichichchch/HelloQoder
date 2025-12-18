"""
Memory Extraction Module
========================

Extracts important information from conversations to store as memories.
Uses LLM to analyze conversations and identify:
- Emotional states
- Important events
- Key concerns
- Relationships mentioned
- Coping strategies
- Goals and aspirations
"""

import json
import httpx
from typing import Optional

from app.config import get_settings
from app.memory.models import MemoryType, MemoryCreateRequest

settings = get_settings()

# Prompt for memory extraction
EXTRACTION_PROMPT = """你是一个心理咨询记忆提取助手。分析以下对话，提取重要信息以便在未来的对话中记住。

对话内容：
用户: {user_message}
咨询师: {assistant_message}

请提取以下类型的记忆（如果存在）：
1. emotion - 用户表达的情绪状态（如：焦虑、悲伤、愤怒、开心等）
2. event - 用户提到的重要事件（如：失业、分手、考试、生病等）
3. concern - 用户的主要担忧和问题
4. relationship - 提到的重要人物关系（如：父母、伴侣、朋友、同事等）
5. coping - 用户使用的应对策略（有效或无效的）
6. goal - 用户的目标或期望
7. insight - 对话中产生的领悟或认识

返回JSON格式：
{
    "memories": [
        {
            "type": "emotion|event|concern|relationship|coping|goal|insight",
            "content": "简洁描述（不超过100字）",
            "importance": 0.1-1.0 (重要性评分),
            "emotion_valence": -1到1 (仅emotion类型需要，负面到正面)
        }
    ]
}

规则：
- 只提取确实存在的信息，不要编造
- 每种类型最多提取1-2条最重要的
- 如果对话中没有值得记住的信息，返回空列表
- importance评分：日常闲聊0.1-0.3，情绪表达0.4-0.6，重大事件0.7-0.9，危机情况1.0
- 用第三人称描述（"用户提到..."而非"我..."）

请只返回JSON，不要其他内容。"""


async def extract_memories_from_conversation(
    user_message: str,
    assistant_message: str,
    user_id: str
) -> list[MemoryCreateRequest]:
    """
    Extract memories from a conversation exchange.
    
    Args:
        user_message: User's message
        assistant_message: AI's response
        user_id: User ID for the memories
        
    Returns:
        List of memory creation requests
    """
    # Skip extraction for very short messages
    if len(user_message) < 10:
        return []
    
    prompt = EXTRACTION_PROMPT.format(
        user_message=user_message,
        assistant_message=assistant_message
    )
    
    try:
        # Call LLM to extract memories
        headers = {
            "Authorization": f"Bearer {settings.mimo_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mimo-v2-flash",
            "messages": [
                {"role": "system", "content": "你是一个专业的心理咨询记忆提取助手，善于从对话中识别重要信息。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,  # Lower temperature for more consistent extraction
            "max_tokens": 512
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.mimo_api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse JSON response
            memories = parse_extraction_response(content, user_id)
            return memories
            
    except Exception as e:
        print(f"[Memory] Extraction error: {e}")
        # Fallback: try simple keyword-based extraction
        return fallback_extraction(user_message, user_id)


def parse_extraction_response(content: str, user_id: str) -> list[MemoryCreateRequest]:
    """Parse the LLM's extraction response."""
    try:
        # Clean up response - sometimes LLM adds markdown
        content = content.strip()
        if content.startswith("```"):
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        
        data = json.loads(content)
        memories = []
        
        for item in data.get("memories", []):
            memory_type_str = item.get("type", "")
            
            # Map string to MemoryType enum
            type_mapping = {
                "emotion": MemoryType.EMOTION,
                "event": MemoryType.EVENT,
                "concern": MemoryType.CONCERN,
                "relationship": MemoryType.RELATIONSHIP,
                "coping": MemoryType.COPING,
                "goal": MemoryType.GOAL,
                "insight": MemoryType.INSIGHT,
            }
            
            memory_type = type_mapping.get(memory_type_str)
            if not memory_type:
                continue
            
            memories.append(MemoryCreateRequest(
                user_id=user_id,
                memory_type=memory_type,
                content=item.get("content", ""),
                importance=float(item.get("importance", 0.5)),
                emotion_valence=item.get("emotion_valence")
            ))
        
        return memories
        
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        print(f"[Memory] Parse error: {e}")
        return []


def fallback_extraction(user_message: str, user_id: str) -> list[MemoryCreateRequest]:
    """
    Simple keyword-based extraction when LLM fails.
    """
    memories = []
    message_lower = user_message.lower()
    
    # Emotion keywords
    emotion_keywords = {
        "焦虑": ("用户表达了焦虑情绪", -0.5),
        "紧张": ("用户感到紧张", -0.4),
        "难过": ("用户感到难过", -0.6),
        "伤心": ("用户感到伤心", -0.7),
        "生气": ("用户感到愤怒", -0.5),
        "开心": ("用户表达了开心的情绪", 0.7),
        "高兴": ("用户感到高兴", 0.6),
        "害怕": ("用户感到恐惧", -0.6),
        "压力": ("用户感受到压力", -0.4),
        "累": ("用户感到疲惫", -0.3),
    }
    
    for keyword, (content, valence) in emotion_keywords.items():
        if keyword in message_lower:
            memories.append(MemoryCreateRequest(
                user_id=user_id,
                memory_type=MemoryType.EMOTION,
                content=content,
                importance=0.5,
                emotion_valence=valence
            ))
            break  # Only one emotion per message
    
    # Event keywords
    event_keywords = {
        "分手": "用户提到经历了分手",
        "失业": "用户提到失业了",
        "裁员": "用户提到被裁员",
        "考试": "用户提到有考试",
        "面试": "用户提到有面试",
        "吵架": "用户提到与人发生争吵",
        "生病": "用户提到身体不适",
        "去世": "用户提到有人去世",
    }
    
    for keyword, content in event_keywords.items():
        if keyword in message_lower:
            memories.append(MemoryCreateRequest(
                user_id=user_id,
                memory_type=MemoryType.EVENT,
                content=content,
                importance=0.7
            ))
            break
    
    # Relationship keywords
    relationship_keywords = {
        "老公": "用户提到了丈夫",
        "老婆": "用户提到了妻子",
        "男朋友": "用户提到了男朋友",
        "女朋友": "用户提到了女朋友",
        "父母": "用户提到了父母",
        "爸爸": "用户提到了父亲",
        "妈妈": "用户提到了母亲",
        "孩子": "用户提到了孩子",
        "领导": "用户提到了工作领导",
        "同事": "用户提到了同事",
    }
    
    for keyword, content in relationship_keywords.items():
        if keyword in message_lower:
            memories.append(MemoryCreateRequest(
                user_id=user_id,
                memory_type=MemoryType.RELATIONSHIP,
                content=content,
                importance=0.4
            ))
            break
    
    return memories


async def generate_session_summary(
    messages: list[dict],
    user_id: str
) -> Optional[MemoryCreateRequest]:
    """
    Generate a summary of the conversation session.
    
    Args:
        messages: List of messages in the session
        user_id: User ID
        
    Returns:
        Memory creation request for the summary, or None
    """
    if len(messages) < 4:  # At least 2 exchanges
        return None
    
    # Format conversation for summarization
    conversation_text = "\n".join([
        f"{'用户' if m['role'] == 'user' else '咨询师'}: {m['content']}"
        for m in messages[-10:]  # Last 10 messages
    ])
    
    summary_prompt = f"""请用2-3句话总结这次心理咨询对话的要点：

{conversation_text}

总结应包括：用户的主要问题、情绪状态、讨论的要点。
用第三人称描述。"""

    try:
        headers = {
            "Authorization": f"Bearer {settings.mimo_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mimo-v2-flash",
            "messages": [
                {"role": "user", "content": summary_prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.mimo_api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            summary = result["choices"][0]["message"]["content"]
            
            return MemoryCreateRequest(
                user_id=user_id,
                memory_type=MemoryType.SUMMARY,
                content=summary,
                importance=0.6
            )
            
    except Exception as e:
        print(f"[Memory] Summary generation error: {e}")
        return None
