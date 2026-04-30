# ── Stage 1: build / dependencias ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Instalar dependencias en un directorio separado para copiar después
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 2: imagen final (más pequeña y segura) ───────────────────────────────
FROM python:3.12-slim

# Hardening básico: usuario no-root
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copiar solo las dependencias instaladas
COPY --from=builder /install /usr/local

# Copiar código fuente
COPY app.py .

# Cambiar propietario
RUN chown -R appuser:appuser /app

# Eliminar herramientas innecesarias (hardening)
RUN apt-get update && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/* /tmp/* /root/.cache

USER appuser

EXPOSE 5000

# Health check integrado en la imagen
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')"

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]
