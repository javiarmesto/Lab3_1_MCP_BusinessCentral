
# MCP_BusinessCentral - Servidor Model Context Protocol 🚀

Este proyecto implementa un **servidor MCP** para Microsoft Business Central, usando FastMCP y FastAPI, integrable con Claude Desktop y otros clientes AI.

## 🌐 Servidor Online Disponible

**🎉 El servidor está desplegado y operativo en Azure App Service:**
- **URL**: https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net
- **Documentación API**: https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/docs
- **Estado**: ✅ 100% funcional con datos reales de Business Central
- **Endpoints disponibles**: GET /customers, /items, /orders, POST /customers

📋 **Para usar el servidor desplegado**: Consulta el archivo `test-mcp-api.http` con ejemplos de todas las operaciones.

## 📋 ¿Qué es MCP?

El **Model Context Protocol** (MCP) es un estándar abierto que permite a clientes AI acceder a herramientas, datos y servicios externos de forma segura y estructurada. MCP define una arquitectura cliente-servidor donde:
- **MCP Host:** Cliente AI (Claude, Copilot, etc.)
- **MCP Client:** Conector MCP en el host
- **MCP Server:** Este proyecto (Python) expone herramientas y lógica de negocio
- **Transporte:** JSON-RPC sobre stdin/stdout (local) o HTTP/SSE (remoto)

Más información: [MCP servers en Microsoft Learn](https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server#about-mcp-servers)
## 🔒 Autenticación y Seguridad

- Se recomienda usar Microsoft Entra ID (Azure AD) y OAuth2 para entornos de producción.
- Consulta la [guía de autenticación para Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-develop-connect-apps).

### Ejemplo: Autenticación OAuth2 con Entra ID

```python
import httpx

def get_bc_token(tenant_id, client_id, client_secret, scope):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": scope
    }
    response = httpx.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]
```
Más información: [Guía de autenticación](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-develop-connect-apps)
## ⚠️ Manejo de límites y errores

- Business Central impone límites de uso (rate limits) en sus APIs. Si recibes errores 429 (Too Many Requests) o 504 (Gateway Timeout), implementa lógica de reintentos y backoff.
- Más información: [Límites de API en Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-rate-limits).

### Ejemplo: Manejo de errores 429 y 504 en llamadas a la API

```python
import httpx
import time

def call_bc_api_with_retry(url, headers, max_retries=5):
    retries = 0
    backoff = 2
    while retries < max_retries:
        response = httpx.get(url, headers=headers)
        if response.status_code == 429:
            wait = backoff ** retries
            print(f"Rate limit alcanzado. Reintentando en {wait}s...")
            time.sleep(wait)
            retries += 1
        elif response.status_code == 504:
            print("Timeout de la API. Reintentando...")
            time.sleep(backoff)
            retries += 1
        else:
            return response
    raise Exception("No se pudo completar la petición tras varios intentos")
```
Más información: [Límites de API en Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-rate-limits)
## 🏅 Buenas prácticas de integración

- Usa siempre los endpoints REST oficiales de Business Central para la integración.
- Desacopla la lógica de negocio del transporte MCP.
- Documenta claramente las herramientas expuestas y sus parámetros siguiendo el estándar MCP.
- Consulta la [documentación de APIs REST de Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/api-overview).

## 🏗️ Estructura del Proyecto

```
📁 MCP_BusinessCentral/
├── requirements.txt            # Dependencias Python
├── README.md                   # Documentación principal
├── .env                        # Variables de entorno (no se incluye en repo)
├── .venv/                      # Entorno virtual Python
├── .github/copilot-instructions.md
├── .vscode/tasks.json          # Tareas de VS Code
├── task1.txt                   # (Ejemplo o pruebas)
└── 📁 bc_server/                # Paquete principal
    ├── BusinessCentralMCP.py   # Servidor MCP (JSON-RPC) para BC
    ├── http_server.py          # API REST (FastAPI) con OpenAPI/Swagger
    ├── setup_guide.py          # Script de validación de entorno y credenciales
    ├── client.py               # Cliente HTTP para la API de BC
    ├── config.py               # Carga y validación de configuración
    └── __init__.py
```


## 🎯 Servidores y APIs Implementados

### **1. BusinessCentralMCP.py - Servidor MCP (JSON-RPC)**
Expone herramientas para interactuar con Business Central vía JSON-RPC:
- **get_customers(limit)**: Lista clientes
- **get_customer_details(customer_id)**: Detalle de un cliente
- **get_items(limit)**: Lista artículos
- **get_sales_orders(limit)**: Lista órdenes de venta
- **create_customer(...)**: Crea un nuevo cliente

### **2. http_server.py - API REST (FastAPI)**
Expone los mismos métodos anteriores vía HTTP REST, con documentación Swagger/OpenAPI.

### **3. setup_guide.py - Validación de entorno**
Script para comprobar variables de entorno y conectividad con Azure AD y Business Central.


## 🛠️ Tecnologías Utilizadas

- **FastMCP**: Framework para servidores MCP (JSON-RPC)
- **FastAPI**: API REST moderna con documentación automática
- **httpx**: Cliente HTTP asíncrono
- **Pydantic**: Validación y serialización de datos
- **python-dotenv**: Gestión de variables de entorno


## 🚀 Instalación y Puesta en Marcha

### 💻 Entorno Local

### 1. Crear entorno virtual
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Instalar dependencias
```powershell
pip install -r requirements.txt
```

### 3. Validar entorno y credenciales
```powershell
python bc_server/setup_guide.py
```

### 4. Lanzar el servidor MCP (JSON-RPC)
```powershell
python -m bc_server.BusinessCentralMCP
```

### 5. Lanzar la API REST (FastAPI)
```powershell
uvicorn bc_server.http_server:app --reload --host 0.0.0.0 --port 8000
```
Accede a la documentación interactiva en: http://localhost:8000/docs

### ☁️ Despliegue en Azure App Service

**¿Quieres el servidor disponible online?** Consulta la **[Guía Completa de Despliegue](./DEPLOYMENT_GUIDE.md)** que incluye:
- Proceso paso a paso para Azure App Service
- Solución a todos los problemas encontrados
- Configuración de variables de entorno
- Scripts de automatización
- Suite de testing completa

**Resultado**: Servidor 100% operativo en Azure con integración real a Business Central.

## 🧪 Testing del Servidor Desplegado

El archivo `test-mcp-api.http` contiene una suite completa de tests para validar todas las funcionalidades:

```http
### Health Check
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/health

### Listar Clientes
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/customers?limit=5

### Crear Cliente
POST https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/customers
Content-Type: application/json

{
  "displayName": "Cliente Test",
  "email": "test@example.com"
}
```

**Usar REST Client extension** de VS Code para ejecutar los tests directamente desde el editor.


## 🔧 Integración con Claude Desktop

1. Localiza el archivo de configuración de Claude Desktop:
   - **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
   - **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Añade una entrada para el servidor MCP de Business Central, por ejemplo:
   ```json
   {
     "mcpServers": {
       "businesscentral-mcp": {
         "command": "C:/ruta/completa/.venv/Scripts/python.exe",
         "args": ["-m", "bc_server.BusinessCentralMCP"]
       }
     }
   }
   ```
3. Reinicia Claude Desktop para que detecte el nuevo servidor MCP.


## 🛠️ Herramientas Disponibles (BusinessCentralMCP)

| Herramienta              | Descripción                                 | Parámetros principales                |
|--------------------------|---------------------------------------------|---------------------------------------|
| get_customers            | Lista clientes de Business Central          | limit (int)                           |
| get_customer_details     | Detalle de un cliente por ID                | customer_id (str)                     |
| get_items                | Lista artículos                             | limit (int)                           |
| get_sales_orders         | Lista órdenes de venta                      | limit (int)                           |
| create_customer          | Crea un nuevo cliente                       | displayName, email, ... (ver código)  |

Consulta la documentación Swagger en `/docs` si usas la API REST.


## 🧪 Testing y Desarrollo

- **Claude Desktop:** Configura el archivo de Claude Desktop y reinicia para probar las herramientas MCP.
- **Modo desarrollo:** Usa los scripts de la carpeta `bc_server` para pruebas y debugging.
- **API REST:** Ejecuta `uvicorn bc_server.http_server:app --reload` y prueba los endpoints en `http://localhost:8000/docs`.
- **VS Code Task:** Usa la tarea "Run Python Script" para lanzar scripts rápidamente.


## 🎯 Casos de Uso Demostrados

- Integración MCP con Business Central
- Exposición de datos de clientes, artículos y órdenes
- Creación de clientes desde herramientas AI
- API REST y JSON-RPC para integración flexible




## 📚 Referencias oficiales y recursos útiles

### 📖 Documentación del Proyecto

| Recurso | Descripción |
|---------|-------------|
| [Guía de Despliegue Azure](./DEPLOYMENT_GUIDE.md) | Proceso completo para llevar el servidor a producción |
| [Suite de Tests](./test-mcp-api.http) | Validación completa de endpoints con REST Client |
| [Configuración MCP](./bc_server/BusinessCentralMCP.py) | Servidor JSON-RPC para integración con AI clients |
| [API REST](./bc_server/http_server.py) | Endpoints HTTP con documentación OpenAPI |

### 🌐 Enlaces Oficiales de Microsoft

- [MCP servers en Microsoft Learn](https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server#about-mcp-servers)
- [APIs REST de Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/api-overview)
- [Desarrollar apps conectadas a Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-develop-connect-apps)
- [Límites de API en Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-rate-limits)
- [Documentación MCP Oficial](https://modelcontextprotocol.io/llms-full.txt)
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [Claude Desktop](https://claude.ai/desktop)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Blog TechSphereDynamics](https://techspheredynamics.com)

| Recurso                                    | Enlace                                                                 |
|--------------------------------------------|------------------------------------------------------------------------|
| MCP servers en Microsoft Learn             | https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server#about-mcp-servers |
| APIs REST de Business Central              | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/api-overview |
| Autenticación y apps conectadas            | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/developer/devenv-develop-connect-apps |
| Límites de API                             | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/dynamics-rate-limits |
| Documentación MCP Oficial                  | https://modelcontextprotocol.io/llms-full.txt |
| FastMCP GitHub                             | https://github.com/jlowin/fastmcp |
| Claude Desktop                             | https://claude.ai/desktop |
| Pydantic Docs                              | https://docs.pydantic.dev/ |
| Blog TechSphereDynamics                    | https://techspheredynamics.com |



---

**¡Desarrollado con visión y buen rollo!** 😉

Para cualquier duda, revisa los comentarios en el código o consulta la documentación oficial de MCP.
