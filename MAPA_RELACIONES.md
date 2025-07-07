# 🗺️ Mapa de relaciones de archivos – MCP Business Central

## Tabla de relaciones y responsabilidades

| Archivo/Fichero                | Importa/Depende de...                | Propósito principal/responsabilidad                                                                 |
|--------------------------------|--------------------------------------|-----------------------------------------------------------------------------------------------------|
| `http_server.py`               | `config`, `client`, `bc_client`,<br>`mcp.server.fastmcp` | Servidor ASGI/HTTP MCP, expone endpoints y herramientas MCP, orquesta ciclo de vida y logging.      |
| `BusinessCentralMCP.py`        | `config`, `client`, `bc_client`,<br>`mcp.server.fastmcp` | Servidor MCP modo CLI/JSON-RPC, expone herramientas MCP para integración con AI vía stdin/stdout.   |
| `client.py`                    | `config`, `azure_auth.token_manager` | Cliente HTTP asíncrono para la API de Business Central, maneja autenticación y lógica de negocio.   |
| `config.py`                    | `.env`, `pydantic`, `dotenv`         | Centraliza la configuración global (Azure AD, BC), valida y expone modelos de configuración.        |
| `azure_auth.py`                | `config`, `httpx`, `datetime`        | Gestiona la autenticación OAuth2/Entra ID, obtiene y refresca tokens para la API de BC.             |
| `bc_server/`                   | (varios, ver README)                 | Carpeta para extensiones, utilidades y documentación específica del servidor MCP.                   |

---

## 🔗 Relaciones clave

- **`http_server.py` y `BusinessCentralMCP.py`**: Ambos son entrypoints MCP, usan las mismas dependencias (`config`, `client`, `bc_client`) y exponen herramientas MCP, pero uno es para HTTP/ASGI y otro para CLI/JSON-RPC.
- **`client.py`**: Es el cliente HTTP central, usado por ambos servidores para acceder a la API de Business Central. Depende de la configuración (`config`) y de la autenticación (`azure_auth`).
- **`config.py`**: Es el núcleo de la configuración, usado por todos los módulos para obtener credenciales y parámetros de entorno.
- **`azure_auth.py`**: Provee el token manager para autenticación, usado por `client.py` para obtener tokens válidos en cada request.
- **`bc_client`**: Es la instancia global de `BusinessCentralClient` definida en `client.py`, importada y usada por los servidores para todas las operaciones de negocio.

---

## 🧭 Flujo típico de una petición

1. **Entrada** (HTTP o CLI) → `http_server.py` o `BusinessCentralMCP.py`
2. **Validación de configuración** → `config.py`
3. **Llamada a herramienta MCP** → función decorada con `@mcp.tool()`
4. **Acceso a datos** → `bc_client` (`client.py`)
5. **Autenticación** → `azure_auth.py` (token_manager)
6. **Respuesta** → Devuelta al cliente (AI, usuario, etc.)

---

## 📚 Notas

- Todos los módulos comparten la configuración global y el cliente HTTP.
- El diseño favorece la separación de responsabilidades y la reutilización de lógica de negocio y autenticación.
- La carpeta `bc_server/` puede contener extensiones, utilidades o documentación adicional, pero no es crítica para el flujo principal.

---

## 📊 Tabla de dependencias (simplificada)

```
http_server.py ─┬─> config.py
                ├─> client.py ──> azure_auth.py
                └─> bc_client (de client.py)
BusinessCentralMCP.py ─┬─> config.py
                       ├─> client.py ──> azure_auth.py
                       └─> bc_client (de client.py)
client.py ──> config.py
client.py ──> azure_auth.py
config.py ──> .env, dotenv, pydantic
azure_auth.py ──> config.py
```

---

## 🖼️ Diagrama visual (ASCII)

```
           +-------------------+
           |   .env/.dotenv    |
           +-------------------+
                    |
              +-----------+
              | config.py |
              +-----------+
                 /      \
                /        \
      +----------------+  
      |  azure_auth.py |  
      +----------------+  
                |           
           +-----------+    
           | client.py |<----------------+
           +-----------+                 |
                |                        |
        +-------------------+            |
        |   bc_client (obj) |            |
        +-------------------+            |
                |                        |
   +-------------------+   +------------------------+
   | http_server.py    |   | BusinessCentralMCP.py  |
   +-------------------+   +------------------------+
                |                        |
         (exponen herramientas MCP vía HTTP/ASGI o CLI/JSON-RPC)
```

---


