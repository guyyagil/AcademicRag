#!/bin/bash
# Wait for Ollama to be ready
echo "Waiting for Ollama to be ready..."
while ! curl -s http://ollama:11434/api/version > /dev/null; do
    sleep 2
done

echo "Ollama is ready. Pulling model..."
curl -X POST http://ollama:11434/api/pull -d '{"name": "nomic-embed-text"}'
echo "Model pulled successfully!"
