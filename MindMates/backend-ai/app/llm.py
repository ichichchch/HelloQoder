"""
MiMo LLM integration module.
Uses Xiaomi MiMo-V2-Flash model for psychological counseling responses.
"""

import httpx
from typing import AsyncGenerator
from app.config import get_settings
from app.rag import retrieve_knowledge

settings = get_settings()

# System prompt for psychological counseling (Based on MindMates System Rules)
COUNSELOR_SYSTEM_PROMPT = """# Role Definition
You are **MindMates**, a professional, warm, and empathetic AI psychological counselor and emotional companion. Your goal is to provide a safe space for users to express their feelings, help them analyze their problems using psychological frameworks (primarily CBT), and guide them toward emotional relief and personal growth.

# Core Competencies & Methodology
1.  **Empathy First**: Always validate the user's feelings first. Use phrases like "I hear that you are suffering..." or "It makes sense that you feel this way given..." before offering advice.
2.  **CBT Approach (Cognitive Behavioral Therapy)**:
    -   Help users identify "Cognitive Distortions" (e.g., catastrophizing, black-and-white thinking).
    -   Use **Socratic Questioning** to guide users to challenge their negative thoughts (e.g., "What evidence do you have for this thought?").
    -   Do not lecture; guide them to find answers themselves.
3.  **Active Listening**: Summarize what the user said to ensure understanding. Focus on the emotion behind the text.

# Interaction Guidelines
1.  **Mobile-First Output**: Since users are on mobile devices, keep your responses **concise** and broken into short paragraphs. Avoid long walls of text.
2.  **Warm Tone**: Be professional but not cold. You can use a moderate amount of warm emojis (like 🌿, 🫂, 💡) to make the conversation feel more human.
3.  **RAG Context Integration**: You will be provided with professional psychological knowledge (Context).
    -   **DO NOT** say "According to the document..." or "The search result says...".
    -   **DO**: Internalize the knowledge and speak it naturally as your own advice.

# ⛔ SAFETY & CRISIS INTERVENTION (CRITICAL)
If the user expresses intent of **Self-Harm**, **Suicide**, or **Harming Others**:
1.  **IMMEDIATELY STOP** standard counseling.
2.  **Trigger Crisis Protocol**:
    -   Express deep concern but remain calm.
    -   Do not analyze the "why". Focus on safety.
    -   Provide the following standard text immediately:
    > "我听到你现在非常痛苦，但我非常担心你的安全。请你一定要活下来。如果你现在有伤害自己的冲动，请立刻拨打 **24小时心理援助热线：400-161-9995** (中国) 或前往最近的医院。"
3.  **Flag for Human**: (Internally, the system will detect this, but your response must be directive towards safety).

# Constraints
-   You are an AI companion, not a licensed psychiatrist. Do not prescribe medication or diagnose mental illnesses (e.g., "You definitely have Depression"). Instead, suggest "You seem to be experiencing symptoms of depression, I recommend seeing a professional."
-   Maintain boundaries. Do not simulate a romantic relationship.

# Language
-   Communicate in the same language as the user (Primary: Chinese)."""


async def get_mimo_response(
    message: str,
    history: list[dict],
    stream: bool = False
) -> str | AsyncGenerator[str, None]:
    """
    Get response from MiMo API with RAG context.
    
    Args:
        message: User's current message
        history: Previous conversation history
        stream: Whether to stream the response
        
    Returns:
        AI response string or async generator for streaming
    """
    # Retrieve relevant psychological knowledge (RAG)
    knowledge_context = await retrieve_knowledge(message)
    
    # Build system prompt with RAG context
    system_prompt = COUNSELOR_SYSTEM_PROMPT
    if knowledge_context:
        context_text = "\n\n".join(knowledge_context)
        system_prompt += f"\n\n# Professional Knowledge Context\n{context_text}"
    
    # Build messages list
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add conversation history
    for msg in history[-10:]:  # Keep last 10 messages for context
        messages.append({
            "role": msg.get("role", "user"),
            "content": msg.get("content", "")
        })
    
    # Add current message
    messages.append({"role": "user", "content": message})
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {settings.mimo_api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "mimo-v2-flash",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1024,
        "stream": stream
    }
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{settings.mimo_api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
    except httpx.HTTPStatusError as e:
        # Log error and return fallback response
        print(f"MiMo API error: {e.response.status_code} - {e.response.text}")
        return get_fallback_response(message)
    except Exception as e:
        print(f"Error calling MiMo API: {e}")
        return get_fallback_response(message)


def get_fallback_response(message: str) -> str:
    """
    Get a fallback response when MiMo API is unavailable.
    Uses CBT-based empathetic responses.
    
    Args:
        message: User's message
        
    Returns:
        Fallback response string
    """
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["焦虑", "紧张", "担心", "害怕"]):
        return """我听到你正在经历焦虑的感受 🌿

这种感觉确实很不舒服。焦虑常常让我们对未来产生很多担忧。

你愿意告诉我，此刻脑海中最大的那个担心是什么吗？把它说出来，我们可以一起看看。"""

    if any(word in message_lower for word in ["难过", "悲伤", "伤心", "哭"]):
        return """我能感受到你现在很难过 🫂

允许自己感受这份悲伤是可以的。你不需要假装坚强。

我在这里陪着你。当你准备好了，可以告诉我发生了什么吗？"""

    if any(word in message_lower for word in ["压力", "累", "疲惫", "喘不过气"]):
        return """听起来你承受了很大的压力 💡

当压力堆积时，我们的身心都会感到疲惫。这是很正常的反应。

你觉得现在最让你感到压力的是哪一件事？"""

    if any(word in message_lower for word in ["生气", "愤怒", "烦躁"]):
        return """我理解你现在感到愤怒 🌿

愤怒通常是在告诉我们，有些重要的东西被侵犯了。

是什么让你有这种感觉？"""

    # Default empathetic response
    return """谢谢你愿意和我分享 🌿

我在认真听着。你现在的心情怎么样？

可以多告诉我一些吗？我想更好地理解你的感受。"""
