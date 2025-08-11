FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev curl     && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt
COPY . /app
ENV GUNICORN_CMD_ARGS="--workers=2 --worker-class=uvicorn.workers.UvicornWorker --timeout=90 --graceful-timeout=45 --bind=0.0.0.0:8080"
EXPOSE 8080
CMD ["gunicorn", "main:app"]
