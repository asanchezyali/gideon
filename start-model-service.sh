#!/usr/bin/env zsh

MODEL=$(grep "DEFAULT_LLM_MODEL" .env | cut -d'=' -f2 | tr -d '"' || echo "llama2")

echo "Starting model services..."
docker model run ai/llama3.2:3B-Q4_K_M

echo "Waiting for Ollama to initialize..."
sleep 10

echo "Pulling model: $MODEL"
curl -X POST http://localhost:11434/api/pull -d "{\"name\": \"$MODEL\"}"

echo "Model setup complete. You can now use: gideon rename auto [directory]"
