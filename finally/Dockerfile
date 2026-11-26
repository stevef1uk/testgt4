FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build
FROM python:3.12-slim
WORKDIR /app
RUN python3 -m pip install --no-cache-dir fastapi==0.115.0 uvicorn==0.30.6
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/out ./frontend/out
EXPOSE 8010
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8010"]