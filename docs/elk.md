# Stack ELK — Documentación

## Componentes

### Elasticsearch
Motor de búsqueda y almacenamiento de logs. Configurado en modo single-node con 512MB de heap para entornos locales.

### Filebeat
Agente ligero que recolecta logs directamente desde los contenedores Docker. Lee los archivos JSON de log en `/var/lib/docker/containers/` y los enriquece con metadatos del contenedor (nombre, imagen, labels).

### Kibana
Interfaz web para explorar y visualizar los logs almacenados en Elasticsearch.

## Uso en Kibana

1. Abrir `http://localhost:5601`
2. Ir a **Stack Management → Data Views → Create data view**
3. Nombre: `App Logs`, Patrón de índice: `filebeat-*`
4. Campo de timestamp: `@timestamp`
5. Guardar y ir a **Discover**

## Campos útiles para filtrar

| Campo | Descripción |
|-------|-------------|
| `container.name` | Nombre del contenedor |
| `log.level` | Nivel del log (info, warning, error) |
| `message` | Contenido del log |
| `event.dataset` | Dataset del evento |

## Ejemplo de query en Kibana

Para ver solo errores de la app:
```
container.name: *app* AND log.level: error
```
