# AI Yoga Coach - backend + frontend (single-port deploy for ai-builders.space)
# Stage 1: build Next.js frontend to static export
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
# Next.js output: 'export' → out/

# Stage 2: FastAPI backend + serve frontend static
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
COPY --from=frontend-builder /app/frontend/out ./static
RUN rm -rf frontend
EXPOSE 8000
CMD sh -c "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"
