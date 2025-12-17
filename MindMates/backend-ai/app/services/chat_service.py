"""
Chat service that orchestrates LLM and crisis detection.
"""

from app.models import ChatRequest, ChatResponse
from app.crisis_detector import detect_crisis
from app.llm import get_mimo_response


async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat request and return an appropriate response.
    
    This function:
    1. Detects if the message indicates a crisis
    2. If crisis, returns immediate help resources
    3. Otherwise, gets a response from the LLM
    
    Args:
        request: The chat request containing message and history
        
    Returns:
        ChatResponse with the AI's response
    """
    # Step 1: Crisis detection
    crisis_result = detect_crisis(request.message)
    
    if crisis_result.is_crisis:
        # Crisis detected - return resources immediately
        # Also get a compassionate response from LLM
        llm_response = await get_mimo_response(
            request.message,
            [msg.model_dump() for msg in request.history]
        )
        
        # Combine crisis resources with compassionate response
        combined_response = f"{llm_response}\n\n---\n\n{crisis_result.crisis_response}"
        
        return ChatResponse(
            content=combined_response,
            intent=crisis_result.intent,
            is_crisis=True
        )
    
    # Step 2: Get LLM response for non-crisis messages
    try:
        response_content = await get_mimo_response(
            request.message,
            [msg.model_dump() for msg in request.history]
        )
        
        return ChatResponse(
            content=response_content,
            intent=crisis_result.intent,
            is_crisis=False
        )
    except Exception as e:
        print(f"Error in chat processing: {e}")
        return ChatResponse(
            content="抱歉，我暂时遇到了一些问题。请稍后再试，或者如果你需要紧急帮助，请拨打心理援助热线：400-161-9995。",
            intent=None,
            is_crisis=False
        )
