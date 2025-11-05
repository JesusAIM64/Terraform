# app/Dockerfile
FROM python:3.10-slim

LABEL maintainer="docente@example.org"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# instalar utilidades mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    bash \
  && rm -rf /var/lib/apt/lists/*

# crear usuario no-root
RUN useradd --create-home --shell /bin/bash appuser

# usar /app como WORKDIR para coincidir con docker-compose si usas ambos enfoques
WORKDIR /app

# Copiar requirements (para cache de Docker)
COPY --chown=appuser:appuser requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pytest pylint

# Copiar el resto de la aplicación
COPY --chown=appuser:appuser . .

# Dar permisos de ejecución y crear directorio de cache con permisos
RUN mkdir -p /app/.pytest_cache && \
    chown -R appuser:appuser /app/.pytest_cache && \
    chmod -R 755 /app/.pytest_cache

USER appuser

EXPOSE 5000

CMD ["./entrypoint.sh"]
