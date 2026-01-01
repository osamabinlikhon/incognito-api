"""
SmolLM2 API Mock with OpenAI and Anthropic Compatibility
This is a lightweight demonstration API that shows the API structure
without requiring heavy ML model loading.

For actual deployment with model inference, consider using:
- HuggingFace Spaces (inferenceapi or gradio widgets)
- Modal (modal.com) - supports Python ML inference
- Railway/Render - full Python support with longer timeouts
"""

import os
import time
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Create FastAPI application
app = FastAPI(
    title="SmolLM2 API (Demo)",
    description="OpenAI and Anthropic compatible API structure for SmolLM2 demonstration",
    version="1.0.0"
)


# ==============================================================================
# Request/Response Models
# ==============================================================================

class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    messages: list[Message]
    max_tokens: int = 512
    temperature: float = 0.7


class AnthropicMessageRequest(BaseModel):
    messages: list[Message]
    max_tokens: int = 512
    temperature: float = 0.7


# ==============================================================================
# OpenAI Compatible Endpoint: /v1/chat/completions
# ==============================================================================

@app.post("/v1/chat/completions", tags=["OpenAI Compatible"])
async def openai_chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.

    Request format matches OpenAI's /v1/chat/completions API.
    Response format is compatible with OpenAI's response structure.
    """
    # Extract the last user message
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if user_messages:
        last_message = user_messages[-1].content
    else:
        last_message = "Hello"

    # Generate a mock response
    mock_response = f"This is a demo response to: {last_message}\n\n"
    mock_response += "To deploy this API with actual SmolLM2 inference, consider using:\n"
    mock_response += "- HuggingFace Spaces (https://huggingface.co/spaces)\n"
    mock_response += "- Modal (https://modal.com)\n"
    mock_response += "- Railway/Render for full Python support"

    # Return OpenAI-compatible response format
    return JSONResponse(content={
        "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "smollm2-135m-instruct",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": mock_response
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": len(last_message.split()),
            "completion_tokens": len(mock_response.split()),
            "total_tokens": len(last_message.split()) + len(mock_response.split())
        }
    })


# ==============================================================================
# Anthropic Compatible Endpoint: /v1/messages
# ==============================================================================

@app.post("/v1/messages", tags=["Anthropic Compatible"])
async def anthropic_messages(request: AnthropicMessageRequest):
    """
    Anthropic-compatible messages endpoint.

    Request format matches Anthropic's /v1/messages API.
    Response format is compatible with Anthropic's response structure.
    """
    # Extract the last user message
    user_messages = [msg for msg in request.messages if msg.role == "user"]
    if user_messages:
        last_message = user_messages[-1].content
    else:
        last_message = "Hello"

    # Generate a mock response
    mock_response = f"This is a demo response to: {last_message}\n\n"
    mock_response += "To deploy this API with actual SmolLM2 inference, consider using:\n"
    mock_response += "- HuggingFace Spaces (https://huggingface.co/spaces)\n"
    mock_response += "- Modal (https://modal.com)\n"
    mock_response += "- Railway/Render for full Python support"

    # Return Anthropic-compatible response format
    return JSONResponse(content={
        "id": f"msg_{uuid.uuid4().hex[:12]}",
        "type": "message",
        "role": "assistant",
        "model": "smollm2-135m-instruct",
        "content": [
            {
                "type": "text",
                "text": mock_response
            }
        ],
        "stop_reason": "end_turn"
    })


# ==============================================================================
# Health Check and Info Endpoints
# ==============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "model": "demo-mode",
        "mode": "mock",
        "note": "This is a demonstration API without actual model inference"
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "SmolLM2 API (Demo)",
        "version": "1.0.0",
        "description": "OpenAI and Anthropic compatible API structure for SmolLM2 demonstration",
        "endpoints": {
            "openai_chat": "/v1/chat/completions",
            "anthropic_messages": "/v1/messages",
            "health": "/health"
        },
        "model": "smollm2-135m-instruct",
        "mode": "demo",
        "note": "For actual inference, deploy to HuggingFace Spaces or Modal"
    }


# ==============================================================================
# Direct Execution
# ==============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
