#!/bin/bash
# =============================================================================
# SmolLM2 API - Complete Setup Script for All Coding Tools
# =============================================================================
# Usage: ./setup_all.sh YOUR_RENDER_URL
# Example: ./setup_all.sh https://my-app.onrender.com
# =============================================================================

URL=$1

if [ -z "$URL" ]; then
    echo "═══════════════════════════════════════════════════════════════════"
    echo "  SmolLM2 API - Setup Script for Coding Tools"
    echo "═══════════════════════════════════════════════════════════════════"
    echo ""
    echo "Usage: $0 YOUR_RENDER_URL"
    echo ""
    echo "Example:"
    echo "  $0 https://my-smollm2-api.onrender.com"
    echo ""
    echo "Steps:"
    echo "  1. Deploy to Render first: https://dashboard.render.com"
    echo "  2. Get your deployment URL"
    echo "  3. Run this script"
    echo ""
    echo "═══════════════════════════════════════════════════════════════════"
    exit 1
fi

echo "═══════════════════════════════════════════════════════════════════"
echo "  SmolLM2 API - Configuration Setup"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "API URL: $URL"
echo ""

# Create config directory
CONFIG_DIR="$HOME/.smolllm2"
mkdir -p "$CONFIG_DIR"

# =============================================================================
# 1. Claude Code Configuration
# =============================================================================
echo "[1/10] Configuring Claude Code..."
mkdir -p "$HOME/.claude"
cat > "$HOME/.claude/settings.json" << EOF
{
  "api_base": "$URL/v1",
  "api_key": "dummy",
  "model": "smollm2-135m-instruct",
  "max_tokens": 2048,
  "temperature": 0.7
}
EOF
echo "  ✓ Claude Code configured"

# =============================================================================
# 2. Cursor Configuration
# =============================================================================
echo "[2/10] Configuring Cursor..."
mkdir -p "$HOME/.cursor"
cat > "$HOME/.cursor/settings.json" << EOF
{
  "api": {
    "openai": {
      "api_base": "$URL/v1",
      "model": "smollm2-135m-instruct"
    }
  }
}
EOF
echo "  ✓ Cursor configured"

# =============================================================================
# 3. Trae Configuration
# =============================================================================
echo "[3/10] Configuring Trae..."
mkdir -p "$HOME/.trae"
cat > "$HOME/.trae/config.json" << EOF
{
  "endpoint": "$URL/v1",
  "model": "smollm2-135m-instruct",
  "temperature": 0.7,
  "max_tokens": 2048
}
EOF
echo "  ✓ Trae configured"

# =============================================================================
# 4. Cline Configuration
# =============================================================================
echo "[4/10] Configuring Cline..."
mkdir -p "$HOME/.cline"
cat > "$HOME/.cline/config.json" << EOF
{
  "provider": "openai",
  "apiBase": "$URL/v1",
  "modelId": "smollm2-135m-instruct",
  "apiKey": "dummy",
  "temperature": 0.7,
  "maxTokens": 2048
}
EOF
echo "  ✓ Cline configured"

# =============================================================================
# 5. Roo Code Configuration
# =============================================================================
echo "[5/10] Configuring Roo Code..."
mkdir -p "$HOME/.roo"
cat > "$HOME/.roo/code.json" << EOF
{
  "models": {
    "smollm2": {
      "model": "smollm2-135m-instruct",
      "apiBase": "$URL/v1",
      "apiKey": "dummy",
      "temperature": 0.7,
      "maxTokens": 2048
    }
  },
  "defaultModel": "smollm2"
}
EOF
echo "  ✓ Roo Code configured"

# =============================================================================
# 6. Codex CLI Configuration
# =============================================================================
echo "[6/10] Configuring Codex CLI..."
mkdir -p "$HOME/.codex"
cat > "$HOME/.codex/config.json" << EOF
{
  "api_base": "$URL/v1",
  "model": "smollm2-135m-instruct",
  "api_key": "dummy"
}
EOF
echo "  ✓ Codex CLI configured"

# =============================================================================
# 7. Grok CLI Configuration
# =============================================================================
echo "[7/10] Configuring Grok CLI..."
mkdir -p "$HOME/.grok"
cat > "$HOME/.grok/config.json" << EOF
{
  "api_base": "$URL/v1",
  "model": "smollm2-135m-instruct",
  "api_key": "dummy"
}
EOF
echo "  ✓ Grok CLI configured"

# =============================================================================
# 8. Kilo Code Configuration
# =============================================================================
echo "[8/10] Configuring Kilo Code..."
mkdir -p "$HOME/.kilocode"
cat > "$HOME/.kilocode/config.json" << EOF
{
  "ai": {
    "provider": "openai",
    "endpoint": "$URL/v1",
    "model": "smollm2-135m-instruct",
    "api_key": "dummy"
  }
}
EOF
echo "  ✓ Kilo Code configured"

# =============================================================================
# 9. Droid Configuration
# =============================================================================
echo "[9/10] Configuring Droid..."
mkdir -p "$HOME/.droid"
cat > "$HOME/.droid/ai_config.json" << EOF
{
  "models": {
    "smollm2": {
      "type": "openai",
      "base_url": "$URL/v1",
      "model": "smollm2-135m-instruct",
      "api_key": "dummy"
    }
  },
  "default": "smollm2"
}
EOF
echo "  ✓ Droid configured"

# =============================================================================
# 10. OpenCode Configuration
# =============================================================================
echo "[10/10] Configuring OpenCode..."
mkdir -p "$HOME/.opencode"
cat > "$HOME/.opencode/config.json" << EOF
{
  "apis": {
    "smollm2": {
      "url": "$URL/v1",
      "model": "smollm2-135m-instruct",
      "token": "dummy"
    }
  },
  "default_api": "smollm2"
}
EOF
echo "  ✓ OpenCode configured"

# =============================================================================
# Environment Variables File
# =============================================================================
cat > "$CONFIG_DIR/environment.sh" << EOF
# SmolLM2 API Environment Variables
# Source this file: source ~/.smolllm2/environment.sh

export SMOLLMW2_API_URL="$URL"
export SMOLLMW2_MODEL="smollm2-135m-instruct"
export SMOLLMW2_API_KEY="dummy"

# OpenAI Compatible
export OPENAI_API_BASE="$URL/v1"
export OPENAI_API_KEY="dummy"

# Anthropic Compatible
export ANTHROPIC_API_BASE="$URL/v1"
export ANTHROPIC_API_KEY="dummy"

# Claude Code
export ANTHROPIC_API_BASE_URL="$URL/v1"

# General
export AI_API_BASE="$URL/v1"
export AI_MODEL="smollm2-135m-instruct"
EOF

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "  ✅ ALL CODING TOOLS CONFIGURED!"
echo "═══════════════════════════════════════════════════════════════════"
echo ""
echo "Configuration saved to: $CONFIG_DIR"
echo ""
echo "To use environment variables, run:"
echo "  source ~/.smolllm2/environment.sh"
echo ""
echo "Test your API with:"
echo "  ./test_api.sh $URL"
echo ""
echo "═══════════════════════════════════════════════════════════════════"
