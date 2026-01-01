#!/usr/bin/env python3
"""
Render Deployment Trigger Script
Usage: python trigger_render_deploy.py <deployment_id>
"""

import sys
import requests
import time

DEPLOYMENT_ID = "rnd_e2t73pNcJBN22jFEEn8e0Sa2d0pL"

def trigger_deploy():
    # Render deployment will download model at runtime
    print("=" * 60)
    print("SMOLLMW2 API RENDER DEPLOYMENT")
    print("=" * 60)
    print(f"
Deployment ID: {DEPLOYMENT_ID}")
    print("
Deployment is configured with:")
    print("- Environment: Python 3")
    print("- Build Command: uv pip install -r requirements.txt")
    print("- Start Command: python src/main.py")
    print("- Model: SmolLM2-135M-Instruct-Q4_K_M.gguf (100MB)")
    print("
The model will be downloaded from HuggingFace at runtime.")
    print("
To complete deployment:")
    print("1. Visit: https://dashboard.render.com/websites/rnd_e2t73pNcJBN22jFEEn8e0Sa2d0pL")
    print("2. Click 'Deploy' to trigger the deployment")
    print("3. Wait for build and model download (~2-5 minutes)")
    print("4. Test endpoints once deployed")
    print("
Expected API endpoints after deployment:")
    print("- GET /health - Health check")
    print("- POST /v1/chat/completions - OpenAI compatible")
    print("- POST /v1/messages - Anthropic compatible")

if __name__ == "__main__":
    trigger_deploy()
