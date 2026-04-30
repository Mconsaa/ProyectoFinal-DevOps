# Pipeline CI/CD — Documentación

## Estructura del pipeline

El archivo `.github/workflows/ci-cd.yml` define 4 jobs que se ejecutan en secuencia:

### Job 1: test
- Instala Python 3.12 y dependencias
- Ejecuta `pytest` con reporte de cobertura de código
- **Bloquea** los siguientes jobs si algún test falla

### Job 2: security-scan
- Construye la imagen Docker localmente en el runner
- **Trivy (imagen):** escanea la imagen en busca de CVEs CRITICAL. Si encuentra alguno, **bloquea el pipeline**
- **Trivy (filesystem):** escanea las dependencias Python. Reporta HIGH/CRITICAL sin bloquear
- **TruffleHog:** detecta secretos hardcodeados en el código. Si encuentra alguno verificado, **bloquea el pipeline**

### Job 3: build (solo rama main)
- Genera versión semántica `1.0.{número de build}`
- Autentica con GitHub Container Registry (GHCR)
- Construye y publica la imagen con múltiples tags: `latest`, `v1.0.X`, `sha-{commit}`

### Job 4: deploy (solo rama main)
- Ejecuta el despliegue con Docker Compose
- Crea un GitHub Release con changelog automático

## Configurar el pipeline en tu repositorio

1. El archivo del workflow debe estar en `.github/workflows/ci-cd.yml`
2. No se necesitan secretos adicionales para el flujo básico (usa `GITHUB_TOKEN` nativo)
3. Para despliegue en servidor remoto, agregar en **Settings → Secrets**:
   - `DEPLOY_HOST`: IP del servidor
   - `DEPLOY_KEY`: llave SSH privada

## Puntos de bloqueo de seguridad

```
Test falla          → ❌ Pipeline detenido
CVE CRITICAL        → ❌ Pipeline detenido  
Secreto en código   → ❌ Pipeline detenido
Todo OK             → ✅ Build → Deploy → Release
```
