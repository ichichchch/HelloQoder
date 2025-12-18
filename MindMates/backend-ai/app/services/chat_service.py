"""
Chat service that orchestrates LLM, crisis detection, and memory system.
"""

from typing import Optional
from app.models import ChatRequest, ChatResponse
from app.crisis_detector import detect_crisis
from app.llm import get_mimo_response
from app.memory import (
    get_memory_service,
    format_memory_context_for_prompt,
)


async def process_chat(request: ChatRequest) -> ChatResponse:
    """
    Process a chat request and return an appropriate response.
    
    This function:
    1. Retrieves relevant memories for context
    2. Detects if the message indicates a crisis
    3. Gets a response from the LLM with memory context
    4. Extracts and stores new memories from the conversation
    
    Args:
        request: The chat request containing message, history, and user_id
        
    Returns:
        ChatResponse with the AI's response
    """
    memory_context_str: Optional[str] = None
    memories_created = 0
    
    # Get memory service
    memory_service = get_memory_service()
    
    # Step 1: Retrieve memory context if user_id is provided
    if request.user_id:
        try:
            memory_context = await memory_service.get_conversation_context(
                user_id=request.user_id,
                current_message=request.message
            )
            memory_context_str = format_memory_context_for_prompt(memory_context)
            
            if memory_context_str:
                print(f"[Memory] Injected context for user {request.user_id[:8]}...")
        except Exception as e:
            print(f"[Memory] Error retrieving context: {e}")
    
    # Step 2: Crisis detection
    crisis_result = detect_crisis(request.message)
    
    if crisis_result.is_crisis:
        # Crisis detected - return resources immediately
        # Also get a compassionate response from LLM
        llm_response = await get_mimo_response(
            request.message,
            [msg.model_dump() for msg in request.history],
            memory_context=memory_context_str
        )
        
        # Combine crisis resources with compassionate response
        combined_response = f"{llm_response}\n\n---\n\n{crisis_result.crisis_response}"
        
        # Store crisis as high-importance memory
        if request.user_id:
            try:
                from app.memory import MemoryType, MemoryCreateRequest, get_memory_store
                store = get_memory_store()
                await store.add_memory(MemoryCreateRequest(
                    user_id=request.user_id,
                    memory_type=MemoryType.EVENT,
                    content=f"用户表达了危机信号：{crisis_result.intent}",
                    importance=1.0,
                    emotion_valence=-0.9
                ))
                memories_created = 1
            except Exception as e:
                print(f"[Memory] Error storing crisis memory: {e}")
        
        return ChatResponse(
            content=combined_response,
            intent=crisis_result.intent,
            is_crisis=True,
            memories_created=memories_created
        )
    
    # Step 3: Get LLM response for non-crisis messages
    try:
        response_content = await get_mimo_response(
            request.message,
            [msg.model_dump() for msg in request.history],
            memory_context=memory_context_str
        )
        
        # Step 4: Extract and store memories from this conversation
        if request.user_id:
            try:
                created_memories = await memory_service.process_conversation_for_memories(
                    user_id=request.user_id,
                    user_message=request.message,
                    assistant_message=response_content
                )
                memories_created = len(created_memories)
                
                if memories_created > 0:
                    print(f"[Memory] Created {memories_created} memories for user {request.user_id[:8]}...")
            except Exception as e:
                print(f"[Memory] Error extracting memories: {e}")
        
        return ChatResponse(
            content=response_content,
            intent=crisis_result.intent,
            is_crisis=False,
            memories_created=memories_created
        )
        
    except Exception as e:
        print(f"Error in chat processing: {e}")
        return ChatResponse(
            content="抱歉，我暂时遇到了一些问题。请稍后再试，或者如果你需要紧急帮助，请拨打心理援助热线：400-161-9995。",
            intent=None,
            is_crisis=False,
            memories_created=0
        )


async def end_chat_session(user_id: str, messages: list[dict]) -> None:
    """
    Called when a chat session ends to generate summary.
    
    Args:
        user_id: User ID
        messages: All messages from the session
    """
    if not user_id or len(messages) < 4:
        return
    
    try:
        memory_service = get_memory_service()
        await memory_service.end_session(user_id, messages)
    except Exception as e:
        print(f"[Memory] Error ending session: {e}")
