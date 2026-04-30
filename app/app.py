import os
import time
import logging
import random
from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import structlog

# ── Configuración de logging estructurado ──────────────────────────────────────
logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
)
logger = structlog.get_logger()

app = Flask(__name__)

# ── Métricas Prometheus ────────────────────────────────────────────────────────
REQUEST_COUNT = Counter(
    "app_requests_total",
    "Total de peticiones HTTP",
    ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "app_request_latency_seconds",
    "Latencia de peticiones HTTP",
    ["endpoint"]
)
ERROR_COUNT = Counter(
    "app_errors_total",
    "Total de errores en la aplicación"
)

# ── Middleware de métricas ─────────────────────────────────────────────────────
@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def record_metrics(response):
    latency = time.time() - request.start_time
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code
    ).inc()
    REQUEST_LATENCY.labels(endpoint=request.path).observe(latency)
    logger.info(
        "request",
        method=request.method,
        path=request.path,
        status=response.status_code,
        latency_ms=round(latency * 1000, 2),
        remote_addr=request.remote_addr,
    )
    return response

# ── Endpoints ──────────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return jsonify({
        "service": "cicd-demo-app",
        "version": os.getenv("APP_VERSION", "1.0.0"),
        "status": "running"
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200

@app.route("/ready")
def ready():
    return jsonify({"status": "ready"}), 200

@app.route("/api/items", methods=["GET"])
def get_items():
    items = [
        {"id": 1, "name": "Item Alpha", "price": 10.5},
        {"id": 2, "name": "Item Beta",  "price": 25.0},
        {"id": 3, "name": "Item Gamma", "price": 7.99},
    ]
    logger.info("items_fetched", count=len(items))
    return jsonify({"items": items, "total": len(items)})

@app.route("/api/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    if item_id < 1 or item_id > 3:
        ERROR_COUNT.inc()
        logger.warning("item_not_found", item_id=item_id)
        return jsonify({"error": "Item no encontrado"}), 404
    return jsonify({"id": item_id, "name": f"Item {item_id}", "price": round(random.uniform(5, 50), 2)})

@app.route("/api/stress")
def stress():
    """Endpoint para simular carga y generar métricas interesantes."""
    time.sleep(random.uniform(0.1, 0.5))
    return jsonify({"message": "stress test completado"})

@app.route("/metrics")
def metrics():
    return generate_latest(), 200, {"Content-Type": CONTENT_TYPE_LATEST}

# ── Arranque ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logger.info("app_starting", port=port)
    app.run(host="0.0.0.0", port=port)
