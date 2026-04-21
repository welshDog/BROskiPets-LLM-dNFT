FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY . /app

RUN python -m pip install --no-cache-dir --upgrade pip && \
    python -m pip install --no-cache-dir fastapi uvicorn[standard] redis httpx web3

EXPOSE 8080

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8080"]
