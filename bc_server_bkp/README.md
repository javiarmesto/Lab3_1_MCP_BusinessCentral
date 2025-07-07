# bc_server - Business Central MCP Server

Este paquete implementa un servidor MCP (Model Context Protocol) y una API REST para exponer funciones de Microsoft Business Central.

## Contenido del paquete

- **config.py**  
  Carga y valida variables de entorno para Azure AD y Business Central (tenant, client, company).

- **client.py**  
  Cliente HTTP asíncrono y resiliente para la API de Business Central. Maneja tokens, reintentos y errores.

- **BusinessCentralMCP.py**  
  Servidor MCP (JSON-RPC por stdin/stdout) usando FastMCP. Registra herramientas:
  - `get_customers(limit: int)`  
  - `get_customer_details(customer_id: str)`  
  - `get_items(limit: int)`  
  - `get_sales_orders(limit: int)`  

- **http_server.py**  
  API REST con FastAPI para los mismos métodos, genera documentación automática en `/docs` y descriptor OpenAPI en `/openapi.json`.

- **setup_guide.py**  
  Script formativo que carga el entorno, valida credenciales de Azure AD y prueba llamadas sencillas a Business Central.

## Requisitos

- Python 3.12
- Módulos (ver `requirements.txt`):
  - fastmcp
  - httpx
  - pydantic
  - fastapi
  - uvicorn
  - python-dotenv

- Variables de entorno (definidas en `.env`):
  ```dotenv
  AZURE_TENANT_ID=...
  AZURE_CLIENT_ID=...
  AZURE_CLIENT_SECRET=...
  BC_ENVIRONMENT=...
  BC_COMPANY_ID=...
  ```

## Instalación y Uso

1. Clonar o ubicarse en el directorio del proyecto.

2. Crear un entorno virtual y activarlo:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Instalar dependencias:
   ```powershell
   pip install -r requirements.txt
   ```

4. Copiar y completar el fichero `.env` con tus credenciales y parámetros de BC.

5. Verificar configuración con el setup guide:
   ```powershell
   python bc_server/setup_guide.py
   ```

6. Iniciar el servidor MCP:
   ```powershell
   python -m bc_server.BusinessCentralMCP
   ```

7. (Opcional) Iniciar la API REST FastAPI:
   ```powershell
   uvicorn bc_server.http_server:app --reload --host 0.0.0.0 --port 8000
   ```

## Herramientas Disponibles

### MCP JSON-RPC
- `get_customers(limit)`  
- `get_customer_details(customer_id)`  
- `get_items(limit)`  
- `get_sales_orders(limit)`  

### FastAPI Endpoints
- **GET** `/customers?limit={limit}`  
- **GET** `/customers/{customer_id}`  
- **GET** `/items?limit={limit}`  
- **GET** `/orders?limit={limit}`  
- **GET** `/health`  

---
*Este README formativo ayuda a entender la arquitectura, instalación y uso del servidor MCP para Business Central.*
