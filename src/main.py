"""
SmolLM2-135M-Instruct API with Full OpenAI and Anthropic Compatibility
Enhanced version with improved multi-turn dialogue, reasoning, and proper model mapping.
"""

import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from llama_cpp import Llama

# ============================================================================
# CONFIGURATION
# ============================================================================

MODEL_PATH = os.environ.get("MODEL_PATH", "model/SmolLM2-135M-Instruct-Q4_K_M.gguf")
CONTEXT_SIZE = int(os.environ.get("CONTEXT_SIZE", 2048))
MAX_TOKENS_DEFAULT = int(os.environ.get("MAX_TOKENS_DEFAULT", 512))
TEMPERATURE_DEFAULT = float(os.environ.get("TEMPERATURE_DEFAULT", 0.7))

# Global model instance
model = None

# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class Message(BaseModel):
    role: str = Field(..., description="Role: system, user, or assistant")
    content: str = Field(..., description="Message content")

class ChatCompletionRequest(BaseModel):
    messages: List[Message]
    model: Optional[str] = None
    max_tokens: Optional[int] = Field(default=MAX_TOKENS_DEFAULT, ge=1, le=2048)
    temperature: Optional[float] = Field(default=TEMPERATURE_DEFAULT, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    stream: Optional[bool] = False
    stop: Optional[List[str]] = None

class AnthropicMessage(BaseModel):
    role: str = Field(..., description="Role: user or assistant")
    content: str = Field(..., description="Message content")

class AnthropicCompletionRequest(BaseModel):
    model: Optional[str] = None
    messages: List[AnthropicMessage]
    max_tokens: Optional[int] = Field(default=MAX_TOKENS_DEFAULT, ge=1, le=2048)
    temperature: Optional[float] = Field(default=TEMPERATURE_DEFAULT, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(default=0.9, ge=0.0, le=1.0)
    stream: Optional[bool] = False
    stop_sequences: Optional[List[str]] = None

# ============================================================================
# MODEL MAPPING
# ============================================================================

# Map internal model names to display names for different APIs
OPENAI_MODEL_MAP = {
    "smollm2-135m-instruct-gguf": "smollm2-135m-instruct",
    "smolllm2-135m-instruct-gguf": "smollm2-135m-instruct",
    "default": "smollm2-135m-instruct"
}

ANTHROPIC_MODEL_MAP = {
    "smollm2-135m-instruct-gguf": "smolllm2-135m-instruct",
    "smolllm2-135m-instruct-gguf": "smolllm2-135m-instruct",
    "default": "smolllm2-135m-instruct"
}

# ============================================================================
# PROMPT TEMPLATES
# ============================================================================

def build_chatml_prompt(messages: List[Message], add_assistant_prompt: bool = True) -> str:
    """
    Build a ChatML-formatted prompt from messages.
    This format is optimal for SmolLM2 instruction tuning.
    
    Args:
        messages: List of message objects with role and content
        add_assistant_prompt: Whether to add the assistant generation prompt
    
    Returns:
        Formatted prompt string
    """
    prompt_parts = []
    
    for msg in messages:
        role = msg.role.lower()
        content = msg.content
        
        # Handle different roles
        if role == "system":
            # System messages set the context
            prompt_parts.append(f"<|im_start|>system\n{content}<|im_end|>")
        elif role == "user":
            prompt_parts.append(f"<|im_start|>user\n{content}<|im_end|>")
        elif role == "assistant":
            # Assistant messages include previous responses for context
            prompt_parts.append(f"<|im_start|>assistant\n{content}<|im_end|>")
        elif role == "function" or role == "tool":
            # Handle function/tool calls
            prompt_parts.append(f"<|im_start|>assistant\n{content}<|im_end|>")
        else:
            # Default to user for unknown roles
            prompt_parts.append(f"<|im_start|>user\n{content}<|im_end|>")
    
    # Add the assistant generation prompt
    if add_assistant_prompt:
        prompt_parts.append("<|im_start|>assistant")
    
    return "\n".join(prompt_parts) + "\n"

def build_anthropic_prompt(messages: List[AnthropicMessage]) -> str:
    """
    Build Anthropic-formatted prompt from messages.
    
    Args:
        messages: List of Anthropic message objects
    
    Returns:
        Formatted prompt string
    """
    prompt_parts = []
    
    for msg in messages:
        role = msg.role.lower()
        content = msg.content
        
        if role == "user":
            prompt_parts.append(f"\n\nHuman: {content}")
        elif role == "assistant":
            prompt_parts.append(f"\n\nAssistant: {content}")
        elif role == "system":
            # Prepend system message
            prompt_parts.insert(0, f"{content}")
    
    # Add final assistant prompt
    prompt_parts.append("\n\nAssistant:")
    
    return "".join(prompt_parts)

# ============================================================================
# MODEL LOADING
# ============================================================================

def load_model():
    """Load the GGUF quantized model with optimized settings."""
    global model
    print(f"Loading model from: {MODEL_PATH}")
    
    model = Llama(
        model_path=MODEL_PATH,
        n_ctx=CONTEXT_SIZE,
        n_threads=4,
        n_gpu_layers=0,  # CPU inference
        verbose=False,
        # Optimization settings
        use_mmap=True,
        use_mlock=False,
        # Context settings
        rope_freq_base=0.0,
        rope_freq_scale=0.0,
    )
    
    print(f"Model loaded successfully! Context size: {CONTEXT_SIZE}")

# ============================================================================
# INFERENCE
# ============================================================================

def generate_response(
    prompt: str,
    max_tokens: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
    stop_tokens: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Generate a response using the SmolLM2 model.
    
    Args:
        prompt: Formatted prompt
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0-2.0)
        top_p: Top-p sampling parameter
        stop_tokens: List of stop tokens
    
    Returns:
        Dictionary with generated text and metadata
    """
    if model is None:
        raise RuntimeError("Model not loaded")
    
    # Default stop tokens
    if stop_tokens is None:
        stop_tokens = [
            "<|im_end|>",
            "<|im_start|>",
            "\nHuman:",
            "\nAssistant:",
            "\nSystem:",
            "User:",
            "Assistant:",
            "System:"
        ]
    
    # Generate
    output = model(
        prompt=prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=stop_tokens,
        echo=False,
        stream=False,
    )
    
    # Extract generated text
    generated_text = output["choices"][0]["text"]
    
    # Count tokens (approximate)
    prompt_tokens = len(model.tokenize(prompt.encode(), add_bos=False))
    completion_tokens = len(model.tokenize(generated_text.encode(), add_bos=False))
    
    return {
        "text": generated_text.strip(),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens
    }

# ============================================================================
# FASTAPI APP
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for model loading."""
    load_model()
    yield
    # Cleanup
    pass

# Create FastAPI application
app = FastAPI(
    title="SmolLM2-135M-Instruct API",
    description="""
    OpenAI and Anthropic compatible API for SmolLM2-135M-Instruct model.
    
    ## Features
    - **OpenAI Compatible**: /v1/chat/completions endpoint
    - **Anthropic Compatible**: /v1/messages endpoint
    - **Multi-turn Dialogue**: Full conversation history support
    - **Streaming**: Non-streaming responses (streaming optional)
    
    ## Model
    - Base Model: HuggingFaceTB/SmolLM2-135M-Instruct
    - Quantization: GGUF Q4_K_M (100MB)
    - Parameters: 135M
    
    ## Endpoints
    - POST /v1/chat/completions - OpenAI format
    - POST /v1/messages - Anthropic format
    - GET /health - Health check
    - GET / - API info
    """,
    version="4.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# OPENAI COMPATIBLE ENDPOINT: /v1/chat/completions
# ============================================================================

@app.post("/v1/chat/completions", tags=["OpenAI Compatible"])
async def openai_chat_completions(request: ChatCompletionRequest):
    """
    OpenAI-compatible chat completions endpoint.
    
    Compatible with OpenAI's /v1/chat/completions API.
    Supports multi-turn conversations and proper response formatting.
    
    Example Usage:
    ```bash
    curl -X POST http://localhost:8000/v1/chat/completions \\
      -H "Content-Type: application/json" \\
      -d '{
        "messages": [
          {"role": "system", "content": "You are a helpful assistant."},
          {"role": "user", "content": "What is AI?"}
        ],
        "max_tokens": 256,
        "temperature": 0.7
      }'
    ```
    """
    try:
        # Validate messages
        if not request.messages:
            raise HTTPException(status_code=400, detail="messages field is required")
        
        # Get parameters
        max_tokens = request.max_tokens or MAX_TOKENS_DEFAULT
        temperature = request.temperature if request.temperature is not None else TEMPERATURE_DEFAULT
        top_p = request.top_p or 0.9
        
        # Build prompt using ChatML format
        prompt = build_chatml_prompt(request.messages)
        
        # Generate response
        result = generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop_tokens=request.stop
        )
        
        # Get mapped model name
        model_name = OPENAI_MODEL_MAP.get("default", "smollm2-135m-instruct")
        
        # Return OpenAI-compatible response
        return JSONResponse(content={
            "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model_name,
            "system_fingerprint": "smolllm2_135m_gguf",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": result["text"]
                    },
                    "finish_reason": "stop",
                    "logprobs": None
                }
            ],
            "usage": {
                "prompt_tokens": result["prompt_tokens"],
                "completion_tokens": result["completion_tokens"],
                "total_tokens": result["total_tokens"]
            }
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ============================================================================
# ANTHROPIC COMPATIBLE ENDPOINT: /v1/messages
# ============================================================================

@app.post("/v1/messages", tags=["Anthropic Compatible"])
async def anthropic_messages(request: AnthropicCompletionRequest):
    """
    Anthropic-compatible messages endpoint.
    
    Compatible with Anthropic's /v1/messages API.
    Supports multi-turn conversations and proper response formatting.
    
    Example Usage:
    ```bash
    curl -X POST http://localhost:8000/v1/messages \\
      -H "Content-Type: application/json" \\
      -d '{
        "messages": [
          {"role": "user", "content": "What is machine learning?"}
        ],
        "max_tokens": 256,
        "temperature": 0.7
      }'
    ```
    """
    try:
        # Validate messages
        if not request.messages:
            raise HTTPException(status_code=400, detail="messages field is required")
        
        # Get parameters
        max_tokens = request.max_tokens or MAX_TOKENS_DEFAULT
        temperature = request.temperature if request.temperature is not None else TEMPERATURE_DEFAULT
        top_p = request.top_p or 0.9
        
        # Build prompt using Anthropic format
        prompt = build_anthropic_prompt(request.messages)
        
        # Generate response
        result = generate_response(
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            stop_tokens=request.stop_sequences
        )
        
        # Get mapped model name
        model_name = ANTHROPIC_MODEL_MAP.get("default", "smolllm2-135m-instruct")
        
        # Return Anthropic-compatible response
        return JSONResponse(content={
            "id": f"msg_{uuid.uuid4().hex[:12]}",
            "type": "message",
            "role": "assistant",
            "model": model_name,
            "content": [
                {
                    "type": "text",
                    "text": result["text"]
                }
            ],
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": result["prompt_tokens"],
                "output_tokens": result["completion_tokens"]
            }
        })
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# ============================================================================
# ADDITIONAL COMPATIBILITY ENDPOINTS
# ============================================================================

@app.get("/v1/models", tags=["Compatibility"])
async def list_models():
    """List available models (OpenAI format)."""
    return JSONResponse(content={
        "object": "list",
        "data": [
            {
                "id": "smollm2-135m-instruct",
                "object": "model",
                "created": 0,
                "owned_by": "HuggingFaceTB"
            }
        ]
    })

@app.get("/v1/model/{model_id}", tags=["Compatibility"])
async def get_model(model_id: str):
    """Get model information (OpenAI format)."""
    return JSONResponse(content={
        "id": model_id,
        "object": "model",
        "created": 0,
        "owned_by": "HuggingFaceTB",
        "permission": [],
        "root": model_id,
        "parent": None
    })

# ============================================================================
# HEALTH CHECK AND INFO ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    model_loaded = model is not None
    model_size = 0
    
    if os.path.exists(MODEL_PATH):
        model_size = round(os.path.getsize(MODEL_PATH) / (1024 * 1024), 2)
    
    return {
        "status": "healthy" if model_loaded else "loading",
        "model_path": MODEL_PATH,
        "model_size_mb": model_size,
        "model_loaded": model_loaded,
        "context_size": CONTEXT_SIZE,
        "api_version": "v1"
    }

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    model_size = 0
    
    if os.path.exists(MODEL_PATH):
        model_size = round(os.path.getsize(MODEL_PATH) / (1024 * 1024), 2)
    
    return {
        "name": "SmolLM2-135M-Instruct API",
        "version": "4.0.0",
        "description": "OpenAI and Anthropic compatible API for SmolLM2-135M-Instruct",
        "model": {
            "name": "smollm2-135m-instruct",
            "size_mb": model_size,
            "parameters": "135M",
            "quantization": "Q4_K_M"
        },
        "endpoints": {
            "openai_chat": "/v1/chat/completions",
            "anthropic_messages": "/v1/messages",
            "models": "/v1/models",
            "health": "/health"
        },
        "docs": {
            "openapi": "/docs",
            "redoc": "/redoc"
        }
    }

# ============================================================================
# DIRECT EXECUTION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
