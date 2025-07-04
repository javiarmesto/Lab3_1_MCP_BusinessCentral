# 🤖 Conector Personalizado para Copilot Studio - Business Central MCP

Esta carpeta contiene todos los archivos necesarios para crear y configurar un conector personalizado en Microsoft Copilot Studio que se integre con nuestro servidor MCP de Business Central.

## 📋 TL;DR

- **Objetivo**: Conectar Copilot Studio con Business Central vía protocolo MCP Streamable
- **Tipo**: Conector MCP (Model Context Protocol) con transporte Streamable
- **URL Base**: https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net
- **Protocolo**: `x-ms-agentic-protocol: mcp-streamable-1.0` (Recomendado por Microsoft)
- **Autenticación**: API Key opcional para producción
- **Herramientas**: 6 herramientas MCP auto-detectadas para agentes conversacionales

---

## 🎯 ¿Qué es un Conector MCP?

Un **conector MCP** (Model Context Protocol) en Copilot Studio permite que tus agentes conversacionales se conecten a servidores MCP externos y ejecuten herramientas específicas de negocio. En nuestro caso:

- **Input**: Preguntas del usuario en lenguaje natural
- **Processing**: Copilot Studio interpreta la intención y llama herramientas MCP
- **MCP Call**: El conector ejecuta herramientas en el servidor Business Central MCP
- **Output**: Respuesta estructurada al usuario

### Ventajas del enfoque MCP

✅ **Protocolo estándar**: Implementa Model Context Protocol oficial  
✅ **Auto-detección**: Herramientas detectadas automáticamente del servidor  
✅ **Streamable transport**: Protocolo recomendado por Microsoft  
✅ **Escalable**: Servidor desplegado en Azure App Service  
✅ **JSON-RPC**: Comunicación estructurada y eficiente  

---

## 📁 Archivos en esta Carpeta

| Archivo | Descripción |
|---------|-------------|
| `business-central-power-platform.yaml` | Esquema YAML optimizado para Power Platform (Recomendado) |
| `business-central-mcp-streamable.yaml` | Esquema YAML MCP Streamable puro (Avanzado) |
| `business-central-mcp-connector.json` | Definición OpenAPI tradicional (referencia) |
| `connector-setup-guide.md` | Guía paso a paso para crear el conector MCP |
| `copilot-studio-actions.md` | Ejemplos de acciones para usar en agentes |
| `testing-scenarios.md` | Casos de prueba y validación |
| `microsoft-compliance-checklist.md` | Verificación de cumplimiento con estándares Microsoft |

---

## 🚀 Proceso de Implementación MCP

### 1. **Preparar el Conector MCP** 📝

- Usar esquema `business-central-mcp-streamable.yaml` (protocolo oficial)
- Configurar transporte MCP Streamable con `x-ms-agentic-protocol: mcp-streamable-1.0`
- Validar herramientas disponibles en el servidor MCP

### 2. **Crear en Copilot Studio** 🔧

- Seguir proceso específico para conectores MCP en Power Platform
- Importar definición YAML MCP Streamable
- Configurar endpoint único `/mcp` para comunicación JSON-RPC
- Probar herramientas MCP básicas

### 3. **Configurar Agente** 🤖

- Crear acciones conversacionales usando herramientas MCP
- Mapear parámetros de herramientas MCP a inputs del usuario
- Configurar respuestas naturales desde datos de Business Central

### 4. **Testing y Validación** ✅

- Casos de prueba completos para herramientas MCP
- Validación de protocolo JSON-RPC
- Optimización de performance y timeouts

---

## 🛠️ Herramientas MCP Disponibles

Nuestro servidor MCP expone las siguientes herramientas listas para usar en Copilot Studio:

### 📊 **Consultas de Datos**

| Operación | Endpoint | Descripción | Parámetros |
|-----------|----------|-------------|------------|
| **Listar Clientes** | `GET /customers` | Obtiene lista de clientes | `limit` (opcional) |
| **Detalle Cliente** | `GET /customers/{id}` | Información específica de un cliente | `customer_id` |
| **Listar Artículos** | `GET /items` | Catálogo de productos/servicios | `limit` (opcional) |
| **Órdenes de Venta** | `GET /orders` | Lista de órdenes de venta | `limit` (opcional) |

### ✏️ **Operaciones de Escritura**

| Operación | Endpoint | Descripción | Parámetros |
|-----------|----------|-------------|------------|
| **Crear Cliente** | `POST /customers` | Registra nuevo cliente | `displayName`, `email`, etc. |

### 🏥 **Utilidades**

| Operación | Endpoint | Descripción | Parámetros |
|-----------|----------|-------------|------------|
| **Health Check** | `GET /health` | Verifica estado del servidor | Ninguno |

---

## 💬 Ejemplos de Conversación

### Consulta de Cliente
```
👤 Usuario: "¿Puedes buscar información del cliente Fabrikam?"

🤖 Copilot: "Voy a buscar información sobre Fabrikam en Business Central..."
          → [Llama a GET /customers?limit=10]
          → [Busca coincidencias con "Fabrikam"]
          
🤖 Copilot: "Encontré el cliente Fabrikam Inc.:
          - ID: 10000
          - Email: contact@fabrikam.com
          - Ciudad: Seattle, WA
          - Estado: Activo"
```

### Creación de Cliente
```
👤 Usuario: "Necesito registrar un nuevo cliente llamado TechCorp"

🤖 Copilot: "Te ayudo a crear el cliente TechCorp. ¿Puedes proporcionarme:
          - Email de contacto
          - Dirección
          - Teléfono?"

👤 Usuario: "Email: info@techcorp.com, ubicados en Madrid"

🤖 Copilot: → [Llama a POST /customers con los datos]
          "✅ Cliente TechCorp creado exitosamente:
          - ID: 50001
          - Nombre: TechCorp  
          - Email: info@techcorp.com
          - Ciudad: Madrid"
```

### Consulta de Inventario
```
👤 Usuario: "¿Qué productos tenemos disponibles?"

🤖 Copilot: → [Llama a GET /items?limit=10]
          "Aquí tienes los productos principales:
          
          📦 **Productos Físicos:**
          - Laptop Business Pro - €1,299
          - Office Chair Deluxe - €450
          
          💼 **Servicios:**
          - Consultoría IT - €120/hora
          - Soporte Premium - €200/mes"
```

---

## 🔐 Configuración de Seguridad

### Opciones de Autenticación

1. **No Authentication** (Desarrollo/Testing)
   - Ideal para pruebas iniciales
   - Sin configuración adicional
   - No recomendado para producción

2. **API Key** (Recomendado)
   - Header personalizado: `X-API-Key`
   - Configurable en Azure App Service
   - Balance entre seguridad y simplicidad

3. **OAuth 2.0** (Máxima Seguridad)
   - Integración con Azure AD
   - Tokens de acceso con expiración
   - Ideal para entornos corporativos

### Implementación de API Key

Si decides usar API Key, modifica el servidor para validar el header:

```python
from fastapi import Header, HTTPException

@app.middleware("http")
async def validate_api_key(request: Request, call_next):
    if request.url.path not in ["/health", "/docs", "/openapi.json"]:
        api_key = request.headers.get("X-API-Key")
        expected_key = os.getenv("API_KEY")
        if not api_key or api_key != expected_key:
            raise HTTPException(status_code=401, detail="Invalid API Key")
    response = await call_next(request)
    return response
```

---

## 🎯 Próximos Pasos

1. **📋 Revisar la [Guía de Configuración](./connector-setup-guide.md)**
2. **🔧 Implementar el conector en Copilot Studio**
3. **🤖 Crear las [Acciones Personalizadas](./copilot-studio-actions.md)**
4. **✅ Ejecutar [Casos de Prueba](./testing-scenarios.md)**
5. **🚀 Desplegar en producción**

---

## 📚 Referencias

| Recurso | URL |
|---------|-----|
| Copilot Studio Connectors | https://learn.microsoft.com/en-us/microsoft-copilot-studio/advanced-custom-connectors |
| OpenAPI Specification | https://swagger.io/specification/ |
| Power Platform Connectors | https://learn.microsoft.com/en-us/connectors/ |
| Business Central APIs | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/ |

---

**🎉 ¡Vamos a crear un agente conversacional que hable directamente con Business Central!** 

Para empezar, sigue la guía de configuración paso a paso.
