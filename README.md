# 🚀 Plataforma Local de CI/CD, Observabilidad y Seguridad

> **Proyecto Final — Ingeniería de Sistemas | Universidad Loyola**  
> Supervisor: M.Sc. Ramiro Jhonatan Pardo Foronda

---

## 📋 Descripción General

Este proyecto implementa una infraestructura local completa que incluye:

- **Aplicación Flask** con endpoints REST y exposición de métricas nativas
- **Pipeline CI/CD** con GitHub Actions (tests → seguridad → build → deploy)
- **Stack ELK** para centralización y visualización de logs
- **Prometheus + Grafana** para monitoreo de métricas y alertas
- **HashiCorp Vault** para gestión segura de secretos
- **Trivy** para escaneo de vulnerabilidades integrado en el pipeline
- **Nginx** como balanceador de carga con 2 instancias de la app
- **Reinicio automático** y health checks en todos los servicios

Todo corre localmente con **Docker Compose**, sin depender de servicios en la nube.

---

## 🏗️ Arquitectura

```
                          ┌──────────────────────────────┐
                          │        CLIENTE / BROWSER      │
                          └──────────────┬───────────────┘
                                         │ :80
                          ┌──────────────▼───────────────┐
                          │         NGINX (LB)            │
                          │    least_conn balancing       │
                          └───────┬──────────┬────────────┘
                                  │          │
                     ┌────────────▼──┐  ┌────▼────────────┐
                     │  Flask App 1  │  │  Flask App 2     │
                     │   :5000       │  │   :5000          │
                     └──────┬────────┘  └──────┬───────────┘
                            │                  │
              ┌─────────────▼──────────────────▼──────────────┐
              │              REDES INTERNAS Docker              │
              └───┬────────────────┬──────────────────┬────────┘
                  │                │                  │
    ┌─────────────▼─────┐  ┌───────▼───────┐  ┌──────▼──────────┐
    │    ELK STACK       │  │  PROMETHEUS   │  │  HASHICORP VAULT │
    │                    │  │  + Grafana    │  │                  │
    │ Filebeat →         │  │  + Alertmgr   │  │  Secretos KV     │
    │ Elasticsearch →    │  │  + NodeExp    │  │  :8200           │
    │ Kibana :5601       │  │  :9090/:3000  │  └──────────────────┘
    └────────────────────┘  └───────────────┘
```

### Componentes y puertos

| Servicio         | Puerto | Descripción                          |
|------------------|--------|--------------------------------------|
| Nginx (LB)       | 80     | Balanceador de carga                 |
| Flask App        | 5000   | Aplicación (acceder vía Nginx)       |
| Kibana           | 5601   | Visualización de logs                |
| Elasticsearch    | 9200   | Motor de búsqueda para logs          |
| Prometheus       | 9090   | Recolección de métricas              |
| Grafana          | 3000   | Dashboards de métricas               |
| Alertmanager     | 9093   | Gestión de alertas                   |
| Node Exporter    | 9100   | Métricas del host                    |
| Vault            | 8200   | Gestión de secretos                  |

---

## ⚡ Inicio Rápido

### Prerequisitos

- Docker Engine ≥ 24.0
- Docker Compose ≥ 2.20
- Git
- 4 GB de RAM disponibles (para ELK)

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/cicd-observabilidad.git
cd cicd-observabilidad
```

### 2. Configurar variables de entorno

```bash
cp .env.example .env
# Editar .env con tus valores (opcional para entorno de prueba)
```

### 3. Levantar toda la infraestructura

```bash
docker compose up -d --build
```

Esperar ~2 minutos para que Elasticsearch esté completamente listo.

### 4. Verificar que todo está corriendo

```bash
docker compose ps
```

Todos los servicios deben mostrar estado `healthy` o `running`.

### 5. Acceder a los servicios

```bash
# Aplicación (vía Nginx)
curl http://localhost/health
curl http://localhost/api/items

# Kibana - visualización de logs
open http://localhost:5601

# Grafana - métricas y dashboards (admin / admin123)
open http://localhost:3000

# Prometheus
open http://localhost:9090

# Vault
open http://localhost:8200
```

---

## 🧪 Pruebas

### Ejecutar tests unitarios localmente

```bash
pip install pytest pytest-cov
pytest app/tests/ -v --cov=app
```

### Generar tráfico para ver métricas

```bash
# Script de prueba de carga básico
for i in $(seq 1 50); do
  curl -s http://localhost/api/items > /dev/null
  curl -s http://localhost/api/items/1 > /dev/null
  curl -s http://localhost/api/stress > /dev/null
  curl -s http://localhost/api/items/999 > /dev/null  # genera errores 404
done
echo "✅ Carga de prueba completada"
```

### Simular caída de un nodo (prueba de alta disponibilidad)

```bash
# Detener una instancia de la app
docker compose stop app

# La app sigue respondiendo vía Nginx con la otra instancia
curl http://localhost/health

# Verificar reinicio automático
docker compose up -d app
```

---

## 📊 Observabilidad

### Stack ELK — Logs

Todos los logs de la aplicación se recolectan automáticamente mediante **Filebeat** y se envían a **Elasticsearch**. Para visualizarlos:

1. Abrir Kibana en `http://localhost:5601`
2. Ir a **Stack Management → Data Views**
3. Crear Data View con patrón `filebeat-*`
4. Ir a **Discover** para explorar los logs en tiempo real

Los logs incluyen: método HTTP, path, status code, latencia en ms, y IP del cliente.

### Prometheus + Grafana — Métricas

La aplicación expone métricas en `/metrics`. Las principales son:

| Métrica | Tipo | Descripción |
|---------|------|-------------|
| `app_requests_total` | Counter | Total de peticiones por método/endpoint/status |
| `app_request_latency_seconds` | Histogram | Latencia con percentiles P50/P95/P99 |
| `app_errors_total` | Counter | Errores de negocio de la aplicación |

El dashboard de Grafana **"Flask App - Métricas"** se provisiona automáticamente.

### Reglas de Alertas

Las siguientes alertas están configuradas en Prometheus:

| Alerta | Condición | Severidad |
|--------|-----------|-----------|
| `HighErrorRate` | >5% de errores 5xx por 2 min | critical |
| `HighLatency` | P95 > 1s por 3 min | warning |
| `AppDown` | Sin métricas por 1 min | critical |
| `HighCPU` | CPU >80% por 5 min | warning |
| `LowMemory` | <15% RAM libre por 5 min | warning |
| `DiskAlmostFull` | Disco >85% por 5 min | warning |

---

## 🔐 Seguridad (DevSecOps)

### Gestión de Secretos con Vault

Los secretos de la aplicación **nunca se exponen en el repositorio**. HashiCorp Vault actúa como fuente de verdad:

```bash
# Ver secretos almacenados (requiere token)
docker exec -it $(docker compose ps -q vault) \
  vault kv get -address=http://localhost:8200 kv/app/config
```

El archivo `.env` está en `.gitignore` y solo existe localmente.

### Escaneo de Vulnerabilidades con Trivy

El pipeline ejecuta Trivy en dos momentos:

1. **Escaneo de imagen Docker** — bloquea el pipeline ante vulnerabilidades CRITICAL
2. **Escaneo del filesystem** — reporta HIGH/CRITICAL en dependencias Python

Para ejecutarlo localmente:

```bash
# Instalar Trivy
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

# Escanear la imagen
docker build -t cicd-demo-app:local ./app
trivy image cicd-demo-app:local

# Escanear dependencias
trivy fs ./app --severity HIGH,CRITICAL
```

### Hardening Aplicado

**En el Dockerfile:**
- Imagen base `python:3.12-slim` (mínima superficie de ataque)
- Build multi-stage (sin herramientas de compilación en la imagen final)
- Usuario no-root (`appuser`) para ejecutar la app
- Eliminación de caché de apt y archivos temporales
- Health check integrado en la imagen

**En Nginx:**
- `server_tokens off` (oculta versión)
- Headers de seguridad: `X-Frame-Options`, `X-Content-Type-Options`, `X-XSS-Protection`
- Límite de tamaño de cuerpo de petición (`client_max_body_size`)

**En el Pipeline:**
- TruffleHog para detectar secretos hardcodeados en el código
- Bloqueo automático del deploy si hay vulnerabilidades CRITICAL
- Tokens de acceso gestionados por GitHub Secrets (nunca en el código)

---

## 🔄 Pipeline CI/CD

El workflow de GitHub Actions (`pipeline/.github/workflows/ci-cd.yml`) tiene 4 etapas:

```
Push a main/develop
       │
       ▼
┌──────────────┐
│  1. TEST     │  pytest + cobertura de código
└──────┬───────┘
       │ ✅ tests pasan
       ▼
┌──────────────┐
│  2. SECURITY │  Trivy (imagen + deps) + TruffleHog
└──────┬───────┘
       │ ✅ sin vulnerabilidades CRITICAL
       ▼
┌──────────────┐
│  3. BUILD    │  docker build + push a GHCR
└──────┬───────┘  versionado semántico: 1.0.{run_number}
       │
       ▼ (solo rama main)
┌──────────────┐
│  4. DEPLOY   │  docker compose up + GitHub Release
└──────────────┘
```

**Puntos de bloqueo de seguridad:**
- ❌ Vulnerabilidad CRITICAL en imagen → pipeline bloqueado
- ❌ Secreto hardcodeado detectado → pipeline bloqueado
- ❌ Test fallido → no se construye ni despliega

---

## ⚙️ Operaciones en Producción

### Alta Disponibilidad

La app corre con **2 réplicas** balanceadas por Nginx. Si una cae, la otra sigue sirviendo tráfico.

Todos los servicios tienen configurado `restart: unless-stopped` o `restart_policy` para reinicio automático ante fallos.

### Health Checks

Cada servicio tiene su propio health check en Docker Compose. Para verificarlos:

```bash
docker compose ps  # muestra estado (healthy/unhealthy)
docker inspect $(docker compose ps -q app) | grep -A5 '"Health"'
```

### Gestión de Releases

Cada push a `main` genera automáticamente:
- Una imagen Docker versionada en GHCR
- Un tag `v1.0.X` en el repositorio
- Un GitHub Release con changelog automático

---

## 🛑 Detener la Infraestructura

```bash
# Detener todo manteniendo los datos
docker compose down

# Detener todo y borrar volúmenes (reset completo)
docker compose down -v
```

---

## 📁 Estructura del Repositorio

```
.
├── app/
│   ├── app.py                    # Aplicación Flask principal
│   ├── requirements.txt          # Dependencias Python
│   ├── Dockerfile                # Imagen multi-stage con hardening
│   └── tests/
│       └── test_app.py           # Tests unitarios
├── infra/
│   ├── nginx/
│   │   └── nginx.conf            # Balanceador de carga
│   ├── elk/
│   │   └── filebeat.yml          # Recolección de logs
│   ├── prometheus/
│   │   ├── prometheus.yml        # Configuración de scraping
│   │   ├── alerts.yml            # Reglas de alertas
│   │   └── alertmanager.yml      # Enrutamiento de alertas
│   ├── grafana/
│   │   ├── datasources.yml       # Fuentes de datos (Prometheus)
│   │   └── dashboards/           # Dashboards JSON
│   └── vault/
│       └── init.sh               # Inicialización de secretos
├── pipeline/
│   └── .github/workflows/
│       └── ci-cd.yml             # Pipeline GitHub Actions
├── docs/                         # Documentación adicional
├── docker-compose.yml            # Orquestación completa
├── .env.example                  # Plantilla de variables de entorno
├── .gitignore
└── README.md                     # Este archivo
```

---

## 📖 Documentación Adicional

- [Configuración detallada de ELK](docs/elk.md)
- [Uso de Vault y gestión de secretos](docs/vault.md)
- [Integración del pipeline CI/CD](docs/pipeline.md)

---

*Universidad Loyola — Carrera de Ingeniería de Sistemas*
