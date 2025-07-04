# 🔧 Guía de Configuración del Conector en Copilot Studio

Esta guía te llevará paso a paso para crear y configurar el conector personalizado de Business Central en Microsoft Copilot Studio.

## 📋 TL;DR

- **Tiempo estimado**: 30-45 minutos
- **Prerrequisitos**: Licencia Copilot Studio, servidor MCP desplegado
- **Resultado**: Conector operativo listo para usar en agentes conversacionales
- **Método**: Importación de definición OpenAPI + configuración visual

---

## 🎯 Prerrequisitos

### Licencias y Accesos Requeridos
- ✅ **Microsoft Copilot Studio** con licencia activa
- ✅ **Power Platform** - Entorno con permisos de administrador
- ✅ **Servidor MCP desplegado** - URL operativa en Azure
- ✅ **Credenciales de Business Central** - Configuradas en Azure App Service

### Verificaciones Previas
```http
# 1. Verificar que el servidor esté operativo
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/health

# 2. Confirmar esquema OpenAPI disponible
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/openapi.json

# 3. Probar endpoint de ejemplo
GET https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/customers?limit=3
```

---

## 🚀 Paso 1: Acceder a Copilot Studio

### 1.1 Navegar al Portal
1. Ir a **[Microsoft Copilot Studio](https://copilotstudio.microsoft.com/)**
2. Iniciar sesión con credenciales corporativas
3. Seleccionar el **entorno apropiado** (Desarrollo/Producción)

### 1.2 Verificar Permisos
- **System Administrator** o **System Customizer** en Power Platform
- **Copilot Studio User** como mínimo
- **Environment Maker** para crear recursos

---

## 🔌 Paso 2: Crear el Conector Personalizado MCP

### 2.1 Proceso Oficial Microsoft para MCP

Según la [documentación oficial de Microsoft](https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp), el proceso para MCP es específico:

1. **Crear un servidor MCP** ✅ (Ya tienes esto desplegado)
2. **Crear conector personalizado MCP** basado en esquema YAML específico  
3. **Consumir vía Copilot Studio** agregando herramientas desde el conector MCP
4. **Publicar el conector** (opcional) para uso multi-tenant

### 2.2 Acceder a la Creación de Conector MCP

**Método Correcto Según Microsoft**:
1. En Copilot Studio, ir a **"Agents"** en navegación izquierda
2. Seleccionar tu agente de la lista
3. Ir a página **"Tools"** de tu agente  
4. Seleccionar **"Add a tool"**
5. Seleccionar **"New tool"**
6. Seleccionar **"Custom connector"** → Te lleva a Power Apps
7. En Power Apps: **"New custom connector"** 
8. Seleccionar **"Import OpenAPI file"**

### 2.3 Importar Definición para MCP

**⚠️ Diferencia Crítica para MCP**: 
Microsoft requiere esquema YAML específico compatible con Power Platform.

**Opción A: Usar Esquema Power Platform Compatible (Recomendado)**
1. Usar el archivo `business-central-power-platform.yaml` 
2. Seleccionar **"Upload file"** 
3. Subir el archivo YAML optimizado para Power Platform
4. Hacer clic en **"Import"**

**Opción B: Esquema MCP Streamable Puro (Avanzado)**
1. Usar el archivo `business-central-mcp-streamable.yaml`
2. ⚠️ **Nota**: Puede requerir ajustes adicionales para compatibilidad

**Si encuentras errores de validación OpenAPI**:
- Usar `business-central-power-platform.yaml` que está optimizado para Power Platform
- Este esquema mantiene funcionalidad MCP pero es compatible con validación de Microsoft

### 2.4 Configurar Información Básica MCP
- **Connector Name**: `Business Central MCP`
- **Description**: `Conector MCP para integrar Business Central vía servidor MCP con transporte Streamable`
- **Host**: `mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net`
- **Base URL**: `/` (raíz)

**⚠️ Diferencias Clave para MCP**:
- **Protocolo**: `x-ms-agentic-protocol: mcp-streamable-1.0`
- **Endpoint único**: `/mcp` (no múltiples endpoints REST)
- **Comunicación**: JSON-RPC sobre HTTP POST
- **Herramientas**: Expuestas automáticamente por el servidor MCP

---

## 🔐 Paso 3: Configurar Autenticación MCP

### 3.1 Opciones de Autenticación para MCP

**Para Desarrollo/Testing:**
- Seleccionar **"No authentication"**
- El servidor MCP maneja la autenticación internamente
- Útil para pruebas iniciales y desarrollo

**Para Producción (Recomendado):**
- Seleccionar **"API Key"**
- **Parameter label**: `API Key Business Central MCP`
- **Parameter name**: `X-API-Key`
- **Parameter location**: `Header`

### 3.2 Implementar Validación API Key en Servidor MCP

Para producción, modifica tu servidor MCP para validar la API Key:

```python
# En bc_server/BusinessCentralMCP.py - Servidor MCP principal
import os
from typing import Optional

class BusinessCentralMCPServer:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        
    async def validate_request(self, headers: dict) -> bool:
        """Validar API Key en requests MCP"""
        if not self.api_key:
            return True  # Sin validación en desarrollo
            
        provided_key = headers.get("X-API-Key")
        return provided_key == self.api_key
    
    async def handle_call(self, request, headers: dict):
        """Manejar llamadas MCP con validación"""
        if not await self.validate_request(headers):
            raise Exception("API Key inválida o faltante")
        
        # Procesar solicitud MCP normalmente
        return await self.process_mcp_request(request)
```

**Configurar en Azure App Service**:
- Variable: `API_KEY`  
- Valor: `bc-mcp-secret-2025-v1` (usar clave segura)

---

## ✅ Paso 4: Validar Herramientas MCP

### 4.1 Herramientas Detectadas Automáticamente

Con MCP, las herramientas se detectan automáticamente desde el servidor:

| Herramienta MCP | Descripción | Parámetros |
|-----------------|-------------|------------|
| `get_customers` | Consultar clientes | `limit` (opcional) |
| `get_customer_details` | Detalle específico cliente | `customer_id` |
| `create_customer` | Crear nuevo cliente | `displayName`, `email`, etc. |
| `get_items` | Catálogo productos | `limit` (opcional) |
| `get_sales_orders` | Órdenes de venta | `limit` (opcional) |
| `health_check` | Estado servidor | Ninguno |

### 4.2 Configuración Automática vs Manual

**✅ Ventaja MCP**: Las herramientas se configuran automáticamente
- **Nombres**: Heredados del servidor MCP
- **Descripciones**: Definidas en el servidor
- **Parámetros**: Validación automática
- **Actualizaciones**: Dinámicas cuando cambia el servidor

**Personalización Opcional**:
- **Visibility**: Marcar herramientas principales como `Important`
- **Friendly Names**: Ajustar nombres para usuarios finales
- **Grouping**: Organizar por categorías (Clientes, Productos, Ventas)

---

## 🧪 Paso 5: Probar el Conector

### 5.1 Ejecutar Pruebas Básicas

1. Ir a la pestaña **"Test"**
2. Hacer clic en **"+ New connection"**
3. Si usas API Key, introducir la clave
4. Hacer clic en **"Create connection"**

### 5.2 Probar Operaciones

**Prueba 1: Health Check**
- Operación: `healthCheck`
- Parámetros: Ninguno
- Resultado esperado: `{"status": "ok"}`

**Prueba 2: Listar Clientes**
- Operación: `getCustomers`
- Parámetros: `limit = 3`
- Resultado esperado: Array con datos de clientes

**Prueba 3: Crear Cliente (Opcional)**
- Operación: `createCustomer`
- Body: 
  ```json
  {
    "displayName": "Cliente Test Conector",
    "email": "test.conector@example.com"
  }
  ```

### 5.3 Validar Respuestas

✅ **Conexión exitosa**: Status 200/201  
✅ **Datos válidos**: Estructura JSON correcta  
✅ **Errores controlados**: Mensajes informativos en fallos  

---

## 🎨 Paso 6: Personalizar para Copilot

### 6.1 Configurar Política de Datos

1. Ir a **"Data"** > **"Data policies"**
2. Clasificar el conector según sensibilidad:
   - **Business**: Para datos internos de la empresa
   - **Confidential**: Si incluye información sensible
   - **General**: Para datos no críticos

### 6.2 Configurar Descripciones Semánticas

Para mejorar la comprensión del AI, enriquecer descripciones:

**Para `getCustomers`:**
```
Busca y obtiene información de clientes registrados en Business Central. 
Útil para consultas como "buscar cliente", "información de empresa", 
"datos de contacto". Permite limitar resultados para búsquedas eficientes.
```

**Para `createCustomer`:**
```
Registra un nuevo cliente en Business Central con datos básicos. 
Requiere al menos nombre de la empresa. Útil cuando el usuario dice 
"crear cliente", "registrar empresa", "dar de alta".
```

### 6.3 Configurar Triggers Semánticos

Para cada operación, agregar **palabras clave** que el AI reconocerá:

| Operación | Triggers Sugeridos |
|-----------|-------------------|
| `getCustomers` | buscar cliente, información empresa, contacto, cliente, empresa |
| `createCustomer` | crear cliente, registrar empresa, nuevo cliente, alta |
| `getCustomerById` | detalle cliente, información específica, datos de |
| `getItems` | productos, artículos, catálogo, inventario, stock |
| `getSalesOrders` | órdenes, ventas, pedidos, facturación |

---

## 🚀 Paso 7: Guardar y Publicar

### 7.1 Guardar Configuración
1. Hacer clic en **"Save"** en la parte superior
2. Confirmar que no hay errores de validación
3. Esperar confirmación de guardado

### 7.2 Publicar el Conector
1. Hacer clic en **"Publish"**
2. Seleccionar **versión** (ej: `1.0.0`)
3. Agregar **notas de versión**:
   ```
   v1.0.0 - Conector inicial Business Central MCP
   - 6 operaciones principales implementadas
   - Integración con datos reales de BC
   - Soporte para consultas y creación
   ```
4. Confirmar publicación

---

## 🤖 Paso 8: Integrar con Agente

### 8.1 Crear Nuevo Agente
1. Ir a **"Copilots"** > **"Create"**
2. Elegir **"New copilot"**
3. Configurar:
   - **Name**: `Asistente Business Central`
   - **Description**: `Ayuda con consultas y gestión de datos de Business Central`
   - **Language**: `Spanish (Spain)`

### 8.2 Agregar el Conector
1. En el agente, ir a **"Actions"**
2. Hacer clic en **"+ Add action"**
3. Seleccionar **"Connector"**
4. Buscar `Business Central MCP`
5. Seleccionar las operaciones deseadas

### 8.3 Configurar Prompts de Sistema

```
Eres un asistente especializado en Microsoft Business Central. 

Puedes ayudar con:
- Buscar información de clientes y empresas
- Consultar el catálogo de productos
- Revisar órdenes de venta
- Registrar nuevos clientes

Cuando el usuario pregunte sobre clientes, empresas o contactos, usa getCustomers.
Para consultas de productos o inventario, usa getItems.
Para información de ventas o pedidos, usa getSalesOrders.
Si necesitan registrar un cliente nuevo, usa createCustomer.

Siempre proporciona respuestas claras y estructuradas en español.
```

---

## 🔍 Paso 9: Testing Final

### 9.1 Conversaciones de Prueba

**Prueba 1: Consulta de Cliente**
```
👤 Usuario: "¿Puedes buscar información de la empresa Fabrikam?"
🤖 Copilot: [Ejecuta getCustomers] "Encontré información de Fabrikam Inc..."
```

**Prueba 2: Catálogo de Productos**
```
👤 Usuario: "¿Qué productos tenemos disponibles?"
🤖 Copilot: [Ejecuta getItems] "Aquí tienes nuestro catálogo..."
```

**Prueba 3: Crear Cliente**
```
👤 Usuario: "Necesito registrar una nueva empresa llamada TechCorp"
🤖 Copilot: [Solicita datos] "¿Puedes proporcionarme email y dirección?"
```

### 9.2 Validar Integración Completa

✅ **Conexiones funcionando**: Sin errores de conectividad  
✅ **Datos correctos**: Información real de Business Central  
✅ **Flujo natural**: Conversaciones fluidas  
✅ **Manejo de errores**: Respuestas apropiadas en fallos  

---

## 🎯 Próximos Pasos

### Mejoras Inmediatas
- [ ] **Configurar más operaciones** (actualizar, eliminar)
- [ ] **Refinar prompts** para mejores respuestas
- [ ] **Agregar validaciones** de entrada
- [ ] **Implementar logging** detallado

### Integración Avanzada
- [ ] **Power Automate flows** para automatizaciones
- [ ] **Power Apps integrations** para interfaces visuales
- [ ] **Teams integration** para colaboración
- [ ] **SharePoint connectors** para documentación

### Monitorización
- [ ] **Usage analytics** en Power Platform
- [ ] **Performance monitoring** del servidor MCP
- [ ] **Error tracking** y alertas
- [ ] **User feedback** y mejoras

---

## 🆘 Troubleshooting

### Problemas Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `Connection timeout` | Servidor no responde | Verificar URL y estado Azure App Service |
| `401 Unauthorized` | API Key incorrecta | Revisar configuración de autenticación |
| `404 Not Found` | Endpoint incorrecto | Validar URLs en definición YAML |
| `500 Internal Error` | Error servidor MCP | Revisar logs Azure y variables entorno |
| **`Parsing error: Operation can have only one body parameter`** | **Esquema YAML incompatible** | **Usar `business-central-power-platform.yaml`** |
| **`ValidationError: The input OpenAPI file is not valid`** | **Formato OpenAPI incorrecto** | **Usar esquema optimizado para Power Platform** |

### Errores Específicos de MCP

**Error: "Operation can have only one body parameter"**
- **Causa**: El esquema YAML tiene múltiples parámetros de cuerpo
- **Solución**: Usar `business-central-power-platform.yaml` que está optimizado para Power Platform
- **Detalle**: OpenAPI 2.0 solo permite un parámetro body por operación

**Error: "The input OpenAPI file is not valid for OpenAPI specification"**
- **Causa**: Extensiones MCP no reconocidas por validador Power Platform
- **Solución**: El esquema `business-central-power-platform.yaml` mantiene funcionalidad MCP pero es compatible
- **Alternativa**: Eliminar extensiones específicas MCP del YAML original

### Logs y Diagnóstico

**Logs del Conector:**
1. Copilot Studio > Connectors > Business Central MCP
2. Pestaña "Analytics"
3. Revisar llamadas recientes y errores

**Logs del Servidor:**
```bash
az webapp log tail --name mcp-bc-javi --resource-group rg-mcp-bc
```

**Validación Manual:**
```bash
# Probar conexión directa
curl -X GET "https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/health"

# Con API Key
curl -X GET "https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/customers?limit=3" \
  -H "X-API-Key: your-secret-key"
```

---

## 📚 Referencias

| Recurso | URL |
|---------|-----|
| Copilot Studio Connectors | https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-custom-connectors |
| Power Platform Connectors | https://learn.microsoft.com/en-us/connectors/custom-connectors/ |
| OpenAPI 3.0 Specification | https://swagger.io/specification/ |
| Power Platform Admin Center | https://admin.powerplatform.microsoft.com/ |

---

**🎉 ¡Conector configurado exitosamente!** 

Tu agente conversacional ya puede hablar directamente con Business Central. ¡Es hora de crear conversaciones inteligentes! 🚀
