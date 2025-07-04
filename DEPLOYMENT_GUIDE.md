# 🚀 Guía de Despliegue a Azure App Service - Business Central MCP Server

Esta guía documenta el proceso completo para desplegar el servidor MCP de Business Central desde un entorno local a Azure App Service, incluyendo todos los problemas encontrados y sus soluciones.

## 📋 TL;DR
- **Objetivo**: Desplegar servidor MCP local a Azure App Service para acceso online
- **Plataforma**: Azure App Service (Linux, Python 3.11)
- **Resultado**: Servidor 100% funcional en https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net
- **Tiempo estimado**: 2-3 horas (incluyendo troubleshooting)

---

## 🎯 Prerrequisitos

### Herramientas necesarias:
- [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli) instalado y configurado
- Python 3.11+ con pip
- VS Code con REST Client extension (para testing)
- Cuenta de Azure con permisos para crear App Services

### Credenciales de Business Central:
- Tenant ID de Azure AD
- Client ID y Client Secret de la aplicación registrada
- Environment name y Company ID de Business Central
- Base URL del entorno de Business Central

---

## 📝 Proceso de Despliegue

### 1. Preparación del Código para Azure

**Modificar `bc_server/http_server.py`** para manejar variables de entorno en Azure:

```python
# Líneas 19-25: Carga condicional de .env
load_dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(load_dotenv_path):
    load_dotenv(load_dotenv_path)
    print(f"✅ Cargado archivo .env desde: {load_dotenv_path}")
else:
    print("ℹ️ No se encontró archivo .env, usando variables de entorno del sistema")
```

**⚠️ Problema identificado**: El código original fallaba en Azure porque buscaba un archivo `.env` que no existe en el contenedor.

**✅ Solución**: Carga condicional que usa variables de entorno del sistema si no existe `.env`.

### 2. Creación del Azure App Service

```bash
# 1. Login en Azure
az login

# 2. Crear Resource Group
az group create --name rg-mcp-bc --location "West Europe"

# 3. Crear App Service Plan (Linux)
az appservice plan create --name plan-mcp-bc --resource-group rg-mcp-bc --sku B1 --is-linux

# 4. Crear App Service con Python 3.11
az webapp create --resource-group rg-mcp-bc --plan plan-mcp-bc --name mcp-bc-javi --runtime "PYTHON|3.11"
```

### 3. Configuración de Variables de Entorno

**Configurar variables en Azure Portal** (App Service > Configuration > Application settings):

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `TENANT_ID` | `tu-tenant-id` | ID del tenant de Azure AD |
| `CLIENT_ID` | `tu-client-id` | ID de la aplicación registrada |
| `CLIENT_SECRET` | `tu-client-secret` | Secret de la aplicación |
| `BC_ENVIRONMENT` | `PRODUCTION` | Nombre del entorno BC |
| `BC_COMPANY_ID` | `tu-company-id` | ID de la compañía en BC |
| `BC_BASE_URL` | `https://api.businesscentral.dynamics.com` | URL base de BC |

**⚠️ Problema crítico**: Las variables de entorno no se configuraron inicialmente, causando errores 500.

**✅ Solución**: Configurar todas las variables en Azure Portal antes del despliegue.

### 4. Preparación del Paquete de Despliegue

**Crear script Python para generar ZIP con rutas Linux**:

```python
# deploy_prep.py
import zipfile
import os

def create_deployment_zip():
    exclude_patterns = ['.env', '.venv', '__pycache__', '.git', '.vs', 'deploy.zip']
    
    with zipfile.ZipFile('deploy.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('.'):
            # Filtrar directorios excluidos
            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
            
            for file in files:
                if not any(pattern in file for pattern in exclude_patterns):
                    file_path = os.path.join(root, file)
                    # CRÍTICO: Usar separadores Linux (/) en lugar de Windows (\)
                    arcname = file_path.replace('\\', '/').lstrip('./')
                    zipf.write(file_path, arcname)
                    print(f"✅ Agregado: {arcname}")

if __name__ == "__main__":
    create_deployment_zip()
    print("🎉 deploy.zip creado exitosamente")
```

**⚠️ Problemas encontrados**:
1. **Separadores de ruta**: Windows usa `\` pero Azure Linux necesita `/`
2. **Archivo .env incluido**: Causaba conflictos con variables de entorno de Azure
3. **Archivos innecesarios**: `.venv`, `__pycache__` aumentaban el tamaño del ZIP

**✅ Soluciones aplicadas**:
1. Convertir `\` a `/` en todos los paths del ZIP
2. Excluir `.env` del paquete de despliegue
3. Filtrar directorios y archivos innecesarios

### 5. Despliegue via Azure CLI

```bash
# Desplegar el ZIP
az webapp deployment source config-zip --resource-group rg-mcp-bc --name mcp-bc-javi --src deploy.zip
```

**⚠️ Errores comunes durante el despliegue**:

| Error | Causa | Solución |
|-------|-------|----------|
| `rsync: [Receiver] failed to set times` | Rutas Windows en ZIP | Usar separadores Linux `/` |
| `ERROR - Container didn't respond to HTTP pings` | Variables de entorno faltantes | Configurar en Azure Portal |
| `ModuleNotFoundError: dotenv` | Dependencias faltantes | Verificar `requirements.txt` |
| `FileNotFoundError: .env` | Código buscando archivo inexistente | Carga condicional de .env |

### 6. Configuración del Startup Command

**En Azure Portal (App Service > Configuration > General settings)**:
```bash
# Startup Command
python -m gunicorn bc_server.http_server:app --bind 0.0.0.0:8000 --worker-class uvicorn.workers.UvicornWorker
```

**⚠️ Problema**: El comando inicial no especificaba el worker class correcto.

**✅ Solución**: Usar `UvicornWorker` para compatibilidad con FastAPI async.

---

## 🧪 Testing y Validación

### Suite de Tests Completa

**Crear archivo `test-mcp-api.http`** para validar todos los endpoints:

```http
### 1. Health Check
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/health

### 2. OpenAPI Schema
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/openapi.json

### 3. Listar Clientes
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/customers?limit=3

### 4. Listar Artículos
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/items?limit=5

### 5. Listar Órdenes
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/orders?limit=3

### 6. Crear Cliente
POST https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/customers
Content-Type: application/json

{
  "displayName": "Cliente Test",
  "email": "test@example.com"
}
```

### Resultados de Validación ✅

| Endpoint | Status | Respuesta |
|----------|--------|-----------|
| `/health` | 200 | `{"status": "ok"}` |
| `/openapi.json` | 200 | Esquema OpenAPI completo |
| `/customers` | 200 | Lista de clientes reales de BC |
| `/items` | 200 | Lista de artículos de BC |
| `/orders` | 200 | Lista de órdenes de venta |
| `POST /customers` | 201 | Cliente creado exitosamente |

---

## 🔧 Troubleshooting Avanzado

### Logs de Azure App Service

**Ver logs en tiempo real**:
```bash
az webapp log tail --name mcp-bc-javi --resource-group rg-mcp-bc
```

**Descargar logs históricos**:
```bash
az webapp log download --name mcp-bc-javi --resource-group rg-mcp-bc
```

### Problemas de Autenticación con Business Central

**Síntomas**: Error 401 "Unauthorized" en llamadas a BC API

**Diagnóstico**:
```python
# Agregar debug en bc_server/client.py
print(f"Token generado: {token[:20]}...")
print(f"Headers: {headers}")
print(f"URL: {url}")
```

**Soluciones comunes**:
1. Verificar que el Client Secret no haya expirado
2. Confirmar scopes correctos en la aplicación Azure AD
3. Validar que la aplicación tenga permisos en Business Central

### Problemas de Conectividad

**Síntomas**: Timeouts o errores de red

**Soluciones**:
1. Verificar firewall de Business Central
2. Confirmar que la IP de Azure App Service esté permitida
3. Revisar configuración de red virtual si aplica

### Problemas de Performance

**Síntomas**: Respuestas lentas o timeouts

**Optimizaciones aplicadas**:
1. Implementar connection pooling en httpx
2. Configurar timeouts apropiados
3. Usar cache para tokens de autenticación

---

## 📊 Monitoring y Mantenimiento

### Azure Application Insights

**Configurar monitoring**:
```bash
# Habilitar Application Insights
az monitor app-insights component create --app mcp-bc-insights --location "West Europe" --resource-group rg-mcp-bc --application-type web

# Vincular con App Service
az webapp config appsettings set --name mcp-bc-javi --resource-group rg-mcp-bc --settings APPINSIGHTS_INSTRUMENTATIONKEY="tu-instrumentation-key"
```

### Métricas Clave a Monitorear

| Métrica | Umbral | Acción |
|---------|---------|---------|
| Response Time | > 5s | Investigar performance |
| Error Rate | > 5% | Revisar logs |
| CPU Usage | > 80% | Escalar plan |
| Memory Usage | > 90% | Optimizar código |

### Backup y Disaster Recovery

**Configurar backups automáticos**:
```bash
az webapp config backup create --resource-group rg-mcp-bc --webapp-name mcp-bc-javi --backup-name daily-backup --frequency 1440 --retain-one true
```

---

## 🎯 Próximos Pasos y Mejoras

### Microsoft Copilot Studio Integration ⭐
- [ ] **[Conector Personalizado](./copilot-studio-connector/)** - Integración directa con agentes conversacionales
- [ ] **Configuración de Actions** - Operaciones específicas para Business Central
- [ ] **Testing de Conversaciones** - Validación de flujos naturales de diálogo
- [ ] **Despliegue en Teams** - Disponibilidad en Microsoft Teams

### Security Hardening
- [ ] Implementar Azure Key Vault para secretos
- [ ] Configurar HTTPS only
- [ ] Habilitar Azure AD authentication para el App Service
- [ ] Implementar rate limiting

### Performance Optimization
- [ ] Configurar CDN para assets estáticos
- [ ] Implementar caching Redis
- [ ] Optimizar queries a Business Central
- [ ] Configurar auto-scaling

### Integration Enhancements
- [ ] Agregar webhooks de Business Central
- [ ] Implementar más operaciones CRUD
- [ ] Conectar con Power Platform
- [ ] Integrar con Azure Logic Apps

### Monitoring & Observability
- [ ] Configurar alerts automáticos
- [ ] Implementar health checks avanzados
- [ ] Crear dashboard de métricas
- [ ] Configurar log analytics

---

## 📚 Referencias y Recursos

| Recurso | URL |
|---------|-----|
| Azure App Service Python | https://docs.microsoft.com/azure/app-service/quickstart-python |
| Business Central API Reference | https://learn.microsoft.com/dynamics365/business-central/dev-itpro/api-reference/v2.0/ |
| FastAPI Deployment Guide | https://fastapi.tiangolo.com/deployment/ |
| Azure CLI Reference | https://docs.microsoft.com/cli/azure/webapp |
| Gunicorn Configuration | https://docs.gunicorn.org/en/stable/configure.html |

---

## ✅ Checklist de Despliegue

- [ ] Código preparado para Azure (carga condicional .env)
- [ ] Azure App Service creado
- [ ] Variables de entorno configuradas
- [ ] ZIP de despliegue generado (rutas Linux)
- [ ] Aplicación desplegada
- [ ] Startup command configurado
- [ ] Health check funcionando
- [ ] Endpoints de Business Central probados
- [ ] Tests de integración completados
- [ ] Monitoring configurado
- [ ] Documentación actualizada

---

**🎉 Resultado Final**: Servidor MCP 100% funcional en Azure, listo para integración con AI agents y Power Platform.

**📧 Contacto**: Para soporte técnico, consulta el [blog TechSphereDynamics](https://techspheredynamics.com) o la documentación oficial de Microsoft.
