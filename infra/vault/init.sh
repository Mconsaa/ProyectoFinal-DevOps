#!/bin/sh
# Script de inicialización de Vault en modo dev
# Se ejecuta una sola vez al arrancar el contenedor

set -e

VAULT_ADDR="http://localhost:8200"
VAULT_TOKEN="${VAULT_TOKEN:-dev-root-token}"

echo "⏳ Esperando que Vault esté disponible..."
until vault status -address="$VAULT_ADDR" > /dev/null 2>&1; do
  sleep 2
done

echo "✅ Vault disponible. Configurando secretos..."

export VAULT_ADDR
export VAULT_TOKEN

# Habilitar el motor KV versión 2
vault secrets enable -address="$VAULT_ADDR" -version=2 kv 2>/dev/null || true

# Guardar secretos de la aplicación
vault kv put -address="$VAULT_ADDR" kv/app/config \
  secret_key="$(openssl rand -hex 32)" \
  db_password="$(openssl rand -hex 16)" \
  api_token="$(openssl rand -hex 24)"

echo "✅ Secretos cargados en Vault:"
vault kv get -address="$VAULT_ADDR" kv/app/config

echo "✅ Vault configurado correctamente."
