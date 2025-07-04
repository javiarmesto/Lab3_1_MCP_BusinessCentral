# 🔧 Solución al Error de Validación OpenAPI

## 🚨 Problema Identificado

Al intentar crear el conector personalizado en Copilot Studio, encontraste este error:

```json
{
  "error": {
    "code": "ValidationError",
    "message": "One or more fields contain incorrect values:",
    "details": [
      {
        "code": "ValidationError",
        "target": "representation",
        "message": "Parsing error(s): Operation can have only one body parameter. Path: paths['/{connectionId}/mcp'].post.parameters[3]"
      }
    ]
  }
}
```

## 🎯 Causa Raíz

**OpenAPI 2.0 Specification Violation**: El esquema YAML original tenía múltiples parámetros en el cuerpo de la operación POST, lo cual viola la especificación OpenAPI 2.0 que usa Power Platform.

### Problemas Específicos:
1. **Múltiples Body Parameters**: OpenAPI 2.0 solo permite UN parámetro de tipo `body` por operación
2. **Extensiones MCP**: Algunas extensiones específicas MCP no son reconocidas por el validador de Power Platform
3. **Estructura Path**: El path original `/mcp` necesitaba el parámetro `{connectionId}` requerido por Power Platform

## ✅ Solución Implementada

### 1. Nuevo Esquema Optimizado

**Archivo**: `business-central-power-platform.yaml`
- ✅ **Un solo parámetro body**: Cumple con OpenAPI 2.0
- ✅ **Path compatible**: Incluye `{connectionId}` requerido por Power Platform  
- ✅ **Estructura MCP**: Mantiene funcionalidad JSON-RPC para MCP
- ✅ **Metadatos Power Platform**: Incluye extensiones `x-ms-*` apropiadas

### 2. Estructura Corregida

**Antes (Problemático)**:
```yaml
parameters:
  - name: mcp-request
    in: body
  - name: other-param  # ❌ SEGUNDO BODY PARAMETER
    in: body
```

**Después (Solucionado)**:
```yaml
parameters:
  - name: connectionId
    in: path
    required: true
  - name: mcpRequest      # ✅ UN SOLO BODY PARAMETER
    in: body
    required: true
```

### 3. JSON-RPC Encapsulado

El esquema ahora encapsula correctamente las solicitudes MCP dentro de un solo objeto:

```json
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "get_customers",
    "arguments": {"limit": 10}
  },
  "id": "req-001"
}
```

## 🔄 Cómo Proceder

### Opción A: Usar Esquema Optimizado (Recomendado)

1. **Archivo a usar**: `business-central-power-platform.yaml`
2. **Ventajas**: 
   - ✅ Compatible 100% con Power Platform
   - ✅ Mantiene funcionalidad MCP completa
   - ✅ Pasa validación OpenAPI 2.0
   - ✅ Incluye metadatos apropiados

### Opción B: Esquema MCP Puro (Solo si necesitas extensiones específicas)

1. **Archivo**: `business-central-mcp-streamable.yaml` (corregido)
2. **Uso**: Solo si necesitas extensiones MCP específicas no soportadas por Power Platform
3. **Nota**: Puede requerir ajustes adicionales

## 📋 Pasos para Implementar

### 1. Eliminar Conector Anterior (Si existe)
```
Power Platform Admin Center > Connectors > Eliminar "Business Central MCP"
```

### 2. Crear Nuevo Conector
1. Usar `business-central-power-platform.yaml`
2. Seguir `connector-setup-guide.md` actualizado
3. Validar que no hay errores de importación

### 3. Probar Funcionalidad
```json
POST /{connectionId}/mcp
{
  "jsonrpc": "2.0",
  "method": "tools/call",
  "params": {
    "name": "health_check",
    "arguments": {}
  },
  "id": "test-001"
}
```

## 🎯 Lecciones Aprendidas

### Validación Power Platform vs MCP

| Aspecto | Power Platform | MCP Puro |
|---------|----------------|----------|
| **OpenAPI Version** | 2.0 Estricto | Flexible |
| **Body Parameters** | Máximo 1 | Sin límite |
| **Extensiones** | Solo `x-ms-*` | Cualquiera |
| **Path Structure** | Requiere `{connectionId}` | Libre |

### Mejores Prácticas

1. **Siempre validar** esquemas OpenAPI con herramientas de Power Platform antes de importar
2. **Usar un solo body parameter** por operación
3. **Incluir metadatos** `x-ms-*` para mejor integración con Copilot Studio
4. **Mantener compatibilidad** OpenAPI 2.0 para máxima compatibilidad

## 🚀 Resultado Esperado

Con el esquema corregido deberías poder:
- ✅ Importar sin errores de validación
- ✅ Conectar con el servidor MCP desplegado
- ✅ Ejecutar herramientas MCP desde Copilot Studio
- ✅ Crear agentes conversacionales funcionales

## 🔗 Referencias

- **Archivo solucionado**: `business-central-power-platform.yaml`
- **Guía actualizada**: `connector-setup-guide.md` (sección troubleshooting)
- **Microsoft Learn**: [Custom Connectors OpenAPI](https://learn.microsoft.com/en-us/connectors/custom-connectors/define-openapi-definition)
- **OpenAPI 2.0 Spec**: [Swagger 2.0 Specification](https://swagger.io/specification/v2/)

---

**🎉 ¡Error resuelto!** Ahora puedes continuar con la creación del conector usando el esquema optimizado para Power Platform.
