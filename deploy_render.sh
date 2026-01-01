#!/bin/bash
# Render Deployment Script
# Usage: bash deploy_render.sh

echo "Preparing Render deployment..."
echo "Render App ID: rnd_e2t73pNcJBN22jFEEn8e0Sa2d0pL"

# Verify files
echo "Checking required files..."
ls -la src/main.py
ls -la requirements.txt
ls -la render.yaml
ls -la model/*.gguf 2>/dev/null || echo "Note: Model will be downloaded at runtime"

echo ""
echo "To deploy to Render:"
echo "1. Go to https://dashboard.render.com"
echo "2. Connect your GitHub repository"
echo "3. Use the render.yaml configuration, OR"
echo "4. Manual setup:"
echo "   - Environment: Python 3"
echo "   - Build Command: uv pip install -r requirements.txt"
echo "   - Start Command: python src/main.py"
echo "   - Environment Variables:"
echo "     - MODEL_PATH=model/SmolLM2-135M-Instruct-Q4_K_M.gguf"
echo "     - PORT=10000"
echo ""
echo "Or use Render API with deployment ID: rnd_e2t73pNcJBN22jFEEn8e0Sa2d0pL"
