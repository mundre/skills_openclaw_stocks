#!/bin/bash
# ollama-memory-setup: Sets up Ollama + nomic-embed-text for OpenClaw memory search
set -e

echo "🔍 Checking Ollama..."

# Install Ollama if missing
if ! command -v ollama &>/dev/null; then
  echo "📦 Installing Ollama..."
  if [[ "$OSTYPE" == "darwin"* ]]; then
    brew install ollama
  else
    curl -fsSL https://ollama.com/install.sh | sh
  fi
else
  echo "✅ Ollama already installed: $(ollama --version 2>/dev/null || echo 'unknown version')"
fi

# Start Ollama
echo "🚀 Starting Ollama..."
if [[ "$OSTYPE" == "darwin"* ]]; then
  brew services start ollama 2>/dev/null || true
  sleep 2
else
  if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
    ollama serve &>/tmp/ollama.log &
    sleep 3
  fi
fi

# Check Ollama is running
if ! curl -s http://localhost:11434/api/tags &>/dev/null; then
  echo "❌ Ollama not responding on port 11434. Try running: ollama serve"
  exit 1
fi
echo "✅ Ollama is running"

# Pull nomic-embed-text
echo "📥 Pulling nomic-embed-text embedding model (~270MB)..."
ollama pull nomic-embed-text
echo "✅ nomic-embed-text ready"

# Patch OpenClaw config
echo "⚙️  Configuring OpenClaw memory search..."
openclaw config set agents.defaults.memorySearch.provider ollama
openclaw config set agents.defaults.memorySearch.model nomic-embed-text
openclaw config set agents.defaults.memorySearch.remote.baseUrl http://localhost:11434
openclaw config set agents.defaults.memorySearch.enabled true
echo "✅ OpenClaw config updated"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next: restart OpenClaw with: openclaw gateway restart"
echo "Then test with: memory_search('test query')"
echo "Expected: response includes \"provider\": \"ollama\""
