# SETUP - Business Central MCP Server

Este documento guía el proceso de configuración y puesta en marcha del servidor MCP y la API REST para Microsoft Business Central.

## 1. Preparar el Entorno

1. Clonar el repositorio o copiar el paquete `bc_server` en tu proyecto.
2. Crear y activar un entorno virtual de Python:
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Instalar las dependencias desde el directorio raíz del proyecto:
   ```powershell
   pip install -r requirements.txt
   ```

## 2. Configurar Variables de Entorno

Copia el archivo `.env.template` al `.env` y completa los valores:
```dotenv
AZURE_TENANT_ID=TU_TENANT_ID          # Identificador de Tenant Azure AD
AZURE_CLIENT_ID=TU_CLIENT_ID          # ID de la aplicación registrada en Azure AD
AZURE_CLIENT_SECRET=TU_CLIENT_SECRET  # Secreto de la aplicación
BC_ENVIRONMENT=environmentId           # Entorno de Business Central ("sandbox", "Production"...)
BC_COMPANY_ID=companyGuid             # GUID de la compañía en BC
```

El servidor cargará este `.env` automáticamente.

## 3. Validar Configuración

Antes de arrancar el servicio, ejecuta `setup_guide.py` para comprobar:
- Carga de variables de entorno
- Autenticación en Azure AD
- Conectividad a Business Central

```powershell
python bc_server/setup_guide.py
```

Si todo es correcto, verás mensajes de éxito.

## 4. Iniciar Servidor MCP (JSON-RPC)

Ejecuta el servidor MCP que expondrá las herramientas por stdin/stdout:
```powershell
python -m bc_server.BusinessCentralMCP
```
La salida esperada indica que está escuchando y listo para recibir llamadas JSON-RPC.

## 5. (Opcional) Ejecutar API REST con FastAPI

Para probar los mismos métodos vía HTTP, lanza:
```powershell
uvicorn bc_server.http_server:app --reload --host 0.0.0.0 --port 8000
```
- Documentación Swagger: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

## 6. Despliegue en Producción

Una vez validado localmente, puedes desplegar en Azure App Service o cualquier plataforma cloud:
```bash
az group create --name mcp-basics-rg --location eastus
az appservice plan create --name CirceBCMCP-plan --resource-group mcp-basics-rg --sku F1
az webapp create --name CirceBCMCP --plan CirceBCMCP-plan --resource-group mcp-basics-rg --runtime "PYTHON|3.12"
az webapp config set --name CirceBCMCP --resource-group mcp-basics-rg --startup-file "python -m uvicorn bc_server.http_server:app --host 0.0.0.0 --port 8000"
# Configurar despliegue local Git y push
``` 

---
*Fin de la guía de setup para el servidor MCP de Business Central.*
