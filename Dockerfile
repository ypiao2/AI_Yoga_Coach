# AI Yoga Coach - deploy to ai-builders.space (Koyeb)
# Per deployment prompt: PORT env var, shell form for CMD, python:3.11-slim
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (see .dockerignore for exclusions)
COPY . .

# PORT is set at runtime by Koyeb
EXPOSE 8000

# Use shell form so ${PORT:-8000} is expanded at runtime
CMD sh -c "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"
