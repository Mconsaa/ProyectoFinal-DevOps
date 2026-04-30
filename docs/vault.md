# HashiCorp Vault — Gestión de Secretos

## ¿Por qué Vault?

Guardar contraseñas y tokens directamente en el código o en variables de entorno sin cifrar es una vulnerabilidad grave. Vault centraliza todos los secretos y controla quién puede acceder a ellos.

## Modo Dev (para este proyecto)

En este entorno local, Vault corre en **modo desarrollo** (los secretos se guardan en memoria, no persisten entre reinicios). Para producción real se usaría modo servidor con backend de almacenamiento persistente.

## Verificar secretos almacenados

```bash
# Acceder a la UI web
open http://localhost:8200
# Token: dev-root-token (o el valor de VAULT_TOKEN en .env)

# Via CLI
docker exec -it $(docker compose ps -q vault) sh
vault login dev-root-token
vault kv get kv/app/config
```

## Agregar nuevos secretos

```bash
docker exec -it $(docker compose ps -q vault) sh
vault kv put kv/app/config nueva_clave="nuevo_valor"
```

## Integración con la app

En un entorno real, la aplicación obtendría los secretos consultando la API de Vault en el arranque:

```python
import hvac

client = hvac.Client(url='http://vault:8200', token=os.getenv('VAULT_TOKEN'))
secret = client.secrets.kv.v2.read_secret_version(path='app/config')
SECRET_KEY = secret['data']['data']['secret_key']
```
