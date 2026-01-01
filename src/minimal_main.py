"""
Ultra-minimal Python HTTP server for Wasmer Edge testing
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import uuid

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "status": "healthy",
                "mode": "minimal",
                "message": "Basic HTTP server working on Wasmer Edge"
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {
                "name": "SmolLM2 API (Minimal)",
                "version": "1.0.0",
                "endpoints": {
                    "health": "/health",
                    "openai_chat": "/v1/chat/completions",
                    "anthropic_messages": "/v1/messages"
                }
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == "/v1/chat/completions":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            response = {
                "id": f"chatcmpl-{uuid.uuid4().hex[:12]}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": "smollm2-135m-instruct",
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a minimal demo response. For actual model inference, use HuggingFace Spaces or Modal."
                    },
                    "finish_reason": "stop"
                }]
            }
            self.wfile.write(json.dumps(response).encode())
        elif self.path == "/v1/messages":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            response = {
                "id": f"msg_{uuid.uuid4().hex[:12]}",
                "type": "message",
                "role": "assistant",
                "model": "smollm2-135m-instruct",
                "content": [{
                    "type": "text",
                    "text": "This is a minimal demo response. For actual model inference, use HuggingFace Spaces or Modal."
                }],
                "stop_reason": "end_turn"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def run():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Starting server on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run()
