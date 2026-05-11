# Multi-stage build: reduce image size from 2.49 GB → ~400 MB

FROM python:3.11-slim as builder

WORKDIR /build

RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn[standard]==0.24.0 \
    redis==5.0.1 \
    httpx==0.26.0 \
    web3==6.15.1 \
    requests==2.31.0 \
    python-dotenv==1.0.0

# ─── Runtime stage ───
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/root/.local/bin:$PATH

# Copy built dependencies from builder
COPY --from=builder /root/.local /root/.local

# Copy only necessary application files (respects .dockerignore)
COPY agent.py metadata.py broski_pet_metadata.py ./
COPY api/ ./api/
COPY eeps/ ./eeps/
COPY rewards/ ./rewards/
COPY config/ ./config/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=30s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health', timeout=5)"

EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
