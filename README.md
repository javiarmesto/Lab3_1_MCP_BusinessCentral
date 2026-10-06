# Lab3_1 · MCP para Business Central

Laboratorio Python que conecta herramientas MCP con las APIs de Business Central mediante credenciales de aplicación de Entra ID. Contiene variantes STDIO y HTTP para estudiar clientes, autenticación y transporte. Es material de aprendizaje; no se ofrece un servicio público mantenido.

## Estado y requisitos

Revisión estática del 6 de octubre de 2026. El despliegue personal citado anteriormente no se ha invocado y su disponibilidad no está acreditada. No se afirma que el proyecto sea «100% funcional» ni que esté listo para producción.

Necesitas Python compatible con las dependencias de [requirements.txt](requirements.txt), pip, un sandbox BC con APIs y una aplicación Entra autorizada en ese sandbox. El repo no fija una versión exacta de Python ni un lock de dependencias. Las versiones mínimas declaradas de MCP/FastMCP no prueban compatibilidad con todas las versiones posteriores.

## Preparar una copia local

```powershell
git clone https://github.com/javiarmesto/Lab3_1_MCP_BusinessCentral.git
cd Lab3_1_MCP_BusinessCentral
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Crea un `.env` local (está ignorado por Git), con los nombres que lee [config.py](config.py):

```dotenv
AZURE_TENANT_ID=<tu-tenant-id>
AZURE_CLIENT_ID=<tu-application-id>
AZURE_CLIENT_SECRET=<tu-secreto-local>
BC_ENVIRONMENT=<tu-sandbox>
BC_COMPANY_ID=<tu-company-id>
LOG_LEVEL=INFO
```

No uses valores de un ZIP histórico. `config.py` construye la URL BC a partir del tenant y del entorno; no consume `BC_BASE_URL`. Revisa con el administrador los permisos de la aplicación y de la compañía.

## Entradas disponibles y resultado esperado

- **STDIO:** `python BusinessCentralMCP.py`, desde la raíz. Los imports son locales (`config`, `client`); no existe el paquete `bc_server/` en el árbol actual. Para un host de escritorio, usa el Python del venv, la ruta absoluta a ese archivo y el directorio de trabajo del repo.
- **HTTP:** `python http_server.py`. La entrada llama a `FastMCP.run(transport="http", host="0.0.0.0", port=8000)`. Expone herramientas MCP; no se ha encontrado una instancia FastAPI llamada `app`, por lo que no uses `uvicorn bc_server.http_server:app` ni presupongas rutas REST `/customers` o `/docs`.
- **Otra variante:** [mcp_stm_server.py](mcp_stm_server.py), con `streamable-http`; estudia sus diferencias antes de elegirla.

El resultado a comprobar con un cliente MCP es descubrir las herramientas y ejecutar **una lectura** de `get_customers` en tu sandbox. `create_customer` escribe datos: solo úsala para un ejercicio explícito con datos de prueba. La entrada STDIO imprime un banner en stdout antes de iniciar MCP; esto puede interferir con clientes JSON-RPC estrictos y queda pendiente de revisión funcional.

## Estructura

| Ruta | Contenido |
|---|---|
| `BusinessCentralMCP.py`, `http_server.py`, `mcp_stm_server.py` | Variantes MCP |
| `client.py`, `azure_auth.py`, `config.py` | API BC, OAuth y configuración |
| `SETUP.md`, `MAPA_RELACIONES.md` | Guías complementarias; contrastar instrucciones históricas con este árbol |
| `bc_server_bkp/` | Implementación y guía de despliegue históricas; se conserva porque contiene documentación única |
| `copilot-studio-connector/` | Material del conector |
| `test_mcp_client.py`, `test-mcp-api.http` | Clientes históricos; revisar sus rutas y destinos antes de ejecutar |

## Empaquetado y límites

Se retiran `deploy.zip` y `recent_logs.zip` del árbol actual: son un paquete generado y logs de un despliegue personal, no dependencias del código. El script crea de nuevo `deploy.zip`; ninguna entrada importa esos ZIP. El historial conserva sus copias.

**No ejecutes `create_deploy_zip.ps1` con secretos locales:** su recorrido no excluye `.env`, `.git` ni logs. Para estudiar un despliegue, prepara el paquete con una lista explícita de los archivos de la variante elegida y `requirements.txt`; deja configuración, credenciales y logs fuera. El script requiere una corrección separada antes de utilizarse como procedimiento fiable.

Antes de exponer HTTP, revisa autenticación de entrada, permisos y transporte. La autenticación de esta aplicación frente a BC no acredita que los clientes del servidor estén autenticados. No se han instalado dependencias, arrancado servidores ni ejecutado endpoints durante esta revisión. No se ha confirmado una licencia aplicable.

[APIs oficiales BC](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/api-overview) · [MCP en Microsoft Learn](https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server#about-mcp-servers) · [TechSphereDynamics](https://techspheredynamics.com).
