# ✅ Casos de Prueba y Validación del Conector

Este archivo contiene una suite completa de casos de prueba para validar que el conector Business Central MCP funciona correctamente en Copilot Studio.

## 📋 TL;DR

- **30+ casos de prueba** organizados por funcionalidad
- **Validación completa** de integración Copilot Studio ↔ Business Central
- **Escenarios reales** de uso empresarial
- **Criterios de aceptación** claros para cada caso

---

## 🎯 Estrategia de Testing

### Niveles de Validación

1. **🔧 Conectividad**: Verificar comunicación básica
2. **📊 Funcionalidad**: Validar cada operación del conector
3. **💬 Conversacional**: Probar flujos de diálogo naturales
4. **🚀 Performance**: Medir tiempos de respuesta
5. **🛡️ Seguridad**: Verificar autenticación y autorización
6. **🔄 Integración**: Validar flujos de trabajo completos

---

## 🔧 Tests de Conectividad

### TC-001: Verificación de Servidor
**Objetivo**: Confirmar que el servidor MCP está operativo

**Pasos**:
1. Abrir Copilot Studio Test
2. Escribir: "¿Está funcionando la conexión con Business Central?"
3. El sistema debe ejecutar healthCheck automáticamente

**Resultado Esperado**:
```
✅ La conexión con Business Central está funcionando correctamente.
Servidor: Operativo ✓
Última verificación: [timestamp]
```

**Criterios de Aceptación**:
- Respuesta en < 3 segundos
- Status 200 del endpoint /health
- Mensaje confirmando operatividad

---

### TC-002: Validación de Autenticación
**Objetivo**: Verificar que la autenticación funciona correctamente

**Configuración**: 
- Si usas API Key, configurar clave incorrecta temporalmente
- Intentar cualquier operación

**Resultado Esperado**:
```
❌ Hay un problema de autenticación con Business Central. 
Por favor, verifica la configuración del conector.
```

**Criterios de Aceptación**:
- Error manejado graciosamente
- Mensaje comprensible para usuarios
- No exposición de detalles técnicos

---

## 📊 Tests de Funcionalidad

### TC-010: Listar Clientes Básico
**Objetivo**: Validar consulta básica de clientes

**Entrada**: "¿Puedes mostrarme algunos clientes?"

**Resultado Esperado**:
```
Aquí tienes algunos de nuestros clientes registrados:

🏢 **Fabrikam Inc.**
- ID: 10000
- Email: contact@fabrikam.com
- Ciudad: Seattle, WA

🏢 **Contoso Ltd.**  
- ID: 20000
- Email: info@contoso.com
- Ciudad: Londres, Reino Unido

🏢 **Adventure Works**
- ID: 30000  
- Email: sales@adventure-works.com
- Ciudad: Bothell, WA

¿Te interesa información específica de algún cliente?
```

**Criterios de Aceptación**:
- Mínimo 3 clientes mostrados
- Información básica presente (nombre, email, ubicación)
- Formateo claro y legible
- Pregunta de seguimiento ofrecida

---

### TC-011: Búsqueda Específica de Cliente
**Objetivo**: Validar búsqueda dirigida por nombre

**Entrada**: "Busca información del cliente Fabrikam"

**Resultado Esperado**:
```
He encontrado información sobre Fabrikam:

📋 **Fabrikam Inc.**
- 🆔 Cliente: 10000
- 📧 Email: contact@fabrikam.com
- 📞 Teléfono: +1-425-555-0100  
- 🌐 Web: www.fabrikam.com
- 📍 Dirección: 123 Main Street, Seattle, WA 98052
- 🏛️ País: Estados Unidos
- 💰 Moneda: USD

¿Necesitas ver las órdenes de este cliente o alguna otra información?
```

**Criterios de Aceptación**:
- Cliente específico encontrado
- Información completa mostrada
- Iconos/formateo visual aplicado
- Opciones de seguimiento ofrecidas

---

### TC-012: Cliente No Encontrado
**Objetivo**: Manejo de búsquedas sin resultados

**Entrada**: "Busca el cliente NoExisteEmpresa"

**Resultado Esperado**:
```
No he encontrado ningún cliente con el nombre "NoExisteEmpresa" en Business Central.

🔍 **Sugerencias:**
- Verifica la ortografía del nombre
- Prueba con nombres parciales (ej: "NoExiste")
- Busca por ciudad o email si los conoces

¿Quieres que haga una búsqueda más amplia o prefieres crear un nuevo cliente?
```

**Criterios de Aceptación**:
- Mensaje claro de "no encontrado"
- Sugerencias constructivas
- Opciones alternativas ofrecidas
- Sin errores técnicos expuestos

---

### TC-020: Consulta de Productos
**Objetivo**: Validar acceso al catálogo de productos

**Entrada**: "¿Qué productos tenemos disponibles?"

**Resultado Esperado**:
```
Aquí tienes nuestro catálogo de productos principales:

## 💻 **Tecnología**
- **Laptop Business Pro** - €1,299.00 (25 unidades)
- **Monitor UltraWide 34"** - €599.00 (12 unidades)

## 🪑 **Mobiliario**
- **Silla Ergonómica Deluxe** - €450.00 (8 unidades)
- **Mesa Ejecutiva** - €899.00 (3 unidades)

## 🛠️ **Servicios**  
- **Consultoría IT** - €120.00/hora
- **Soporte Premium** - €200.00/mes

¿Te interesa información específica de algún producto?
```

**Criterios de Aceptación**:
- Productos categorizados lógicamente
- Precios y stock mostrados
- Diferentes tipos (productos/servicios) incluidos
- Formateo claro con emojis/símbolos

---

### TC-021: Búsqueda Específica de Producto
**Objetivo**: Validar consulta dirigida de inventario

**Entrada**: "¿Tenemos laptops disponibles y a qué precio?"

**Resultado Esperado**:
```
Sí, tenemos varios modelos de laptops disponibles:

💻 **Laptops en Stock:**

**Laptop Business Pro**
- 💰 Precio: €1,299.00
- 📦 Stock: 25 unidades  
- ✅ Disponibilidad: Inmediata

**Laptop Student Edition**
- 💰 Precio: €899.00
- 📦 Stock: 15 unidades
- ✅ Disponibilidad: Inmediata

¿Necesitas especificaciones técnicas o información sobre descuentos por volumen?
```

**Criterios de Aceptación**:
- Productos relevantes encontrados
- Información de precio y stock
- Indicadores de disponibilidad
- Preguntas de seguimiento apropiadas

---

### TC-030: Consulta de Órdenes de Venta
**Objetivo**: Validar acceso a datos de ventas

**Entrada**: "¿Cuáles son las últimas órdenes de venta?"

**Resultado Esperado**:
```
Aquí tienes las órdenes de venta más recientes:

## 📋 **Órdenes Activas**

**🔸 Orden SO-2025-001**  
- 👤 Cliente: Fabrikam Inc.
- 📅 Fecha: 15 enero 2025
- 💰 Total: €1,935.99 (IVA incluido)
- 📈 Estado: Abierta

**🔸 Orden SO-2025-002**
- 👤 Cliente: Contoso Ltd.  
- 📅 Fecha: 14 enero 2025
- 💰 Total: €2,450.00 (IVA incluido)
- 📈 Estado: Liberada

**💰 Total en órdenes activas: €4,385.99**

¿Quieres ver detalles de alguna orden específica?
```

**Criterios de Aceptación**:
- Mínimo 2-3 órdenes mostradas
- Información clave visible (cliente, fecha, total, estado)
- Resumen/totales incluidos
- Opciones de drill-down ofrecidas

---

### TC-040: Crear Cliente - Flujo Exitoso
**Objetivo**: Validar creación completa de cliente nuevo

**Conversación Completa**:
```
👤 "Necesito crear un nuevo cliente llamado TechSphere Solutions"

🤖 "Perfecto, te ayudo a registrar TechSphere Solutions. Necesito algunos datos:
- ✅ Nombre: TechSphere Solutions  
- 📧 Email de contacto
- 📍 Ubicación  
- 🏛️ Información fiscal (opcional)

¿Puedes proporcionarme el email y la ciudad?"

👤 "Email: info@techsphere.com, están en Valencia"

🤖 "Excelente. ¿Tienes la dirección completa y el NIF/CIF?"

👤 "Dirección: Calle Colón 45, Valencia. CIF: B98765432"

🤖 [Ejecuta createCustomer]
"¡✅ Cliente creado exitosamente!

🎉 **TechSphere Solutions**
- 🆔 ID: CUST-50001
- 📧 Email: info@techsphere.com  
- 📍 Dirección: Calle Colón 45, Valencia
- 🏛️ CIF: B98765432
- 💰 Moneda: EUR
- 📅 Registrado: Hoy

¿Quieres crear una orden de venta para este cliente?"
```

**Criterios de Aceptación**:
- Flujo conversacional natural
- Validación de datos requeridos
- Confirmación de creación exitosa
- ID asignado correctamente
- Siguientes pasos sugeridos

---

### TC-041: Crear Cliente - Datos Mínimos
**Objetivo**: Validar creación con información básica

**Entrada**: "Crear cliente MinimalCorp con email minimal@corp.com"

**Resultado Esperado**:
```
✅ He creado el cliente MinimalCorp con los datos proporcionados:

🏢 **MinimalCorp**
- 🆔 ID: CUST-50002
- 📧 Email: minimal@corp.com
- 💰 Moneda: EUR (por defecto)
- 📅 Registrado: Hoy

ℹ️ **Nota:** Puedes completar más información (dirección, teléfono, etc.) cuando esté disponible.

¿Necesitas hacer algo más con este cliente?
```

**Criterios de Aceptación**:
- Creación exitosa con datos mínimos
- Valores por defecto aplicados apropiadamente
- Nota sobre información adicional
- Cliente funcional para transacciones

---

## 💬 Tests Conversacionales

### TC-050: Flujo Multi-step
**Objetivo**: Validar conversaciones complejas con múltiples pasos

**Conversación**:
```
👤 "¿Qué cliente ha comprado más últimamente?"

🤖 [Analiza órdenes] "Según las órdenes recientes, Fabrikam Inc. tiene el mayor volumen:
- 3 órdenes en enero 2025  
- Total: €5,235.50
- Último pedido: Laptop Business Pro x2

¿Quieres ver el detalle de sus compras?"

👤 "Sí, y también qué productos les interesan más"

🤖 [Profundiza en análisis] "Fabrikam Inc. muestra preferencia por:

📊 **Patrones de Compra:**
- 60% Tecnología (laptops, monitores)
- 30% Servicios (consultoría IT)  
- 10% Mobiliario

**Productos favoritos:**
- Laptop Business Pro (5 unidades últimos 3 meses)
- Consultoría IT (40 horas/mes promedio)

¿Te interesa contactarlos para una propuesta de servicios extendidos?"
```

**Criterios de Aceptación**:
- Análisis inteligente de datos
- Respuestas contextuales apropiadas
- Insights de negocio útiles
- Sugerencias proactivas de acciones

---

### TC-051: Manejo de Ambigüedad
**Objetivo**: Gestión de consultas ambiguas o imprecisas

**Entrada**: "Busca algo sobre ventas"

**Resultado Esperado**:
```
Tu consulta sobre "ventas" puede referirse a varias cosas. ¿Te interesa:

🎯 **Opciones disponibles:**
1. 📊 **Órdenes de venta recientes** - Últimos pedidos y su estado
2. 👥 **Clientes por volumen** - Quién compra más
3. 📦 **Productos más vendidos** - Top artículos
4. 📈 **Resumen de ventas** - Métricas y totales
5. 🔍 **Buscar orden específica** - Por número o cliente

¿Cuál de estas opciones te interesa más?
```

**Criterios de Aceptación**:
- Reconocimiento de ambigüedad
- Opciones claras presentadas
- Categorización lógica
- Facilita la elección del usuario

---

## 🚀 Tests de Performance

### TC-060: Tiempo de Respuesta Básico
**Objetivo**: Validar tiempos de respuesta aceptables

**Mediciones**:
- ✅ Health check: < 2 segundos
- ✅ getCustomers (5 resultados): < 5 segundos  
- ✅ getItems (10 resultados): < 6 segundos
- ✅ getSalesOrders (5 resultados): < 7 segundos
- ✅ createCustomer: < 8 segundos

**Criterios de Aceptación**:
- Ninguna operación > 10 segundos
- Indicadores de "procesando" para operaciones > 3 segundos
- Timeouts manejados graciosamente

---

### TC-061: Carga Concurrent
**Objetivo**: Validar comportamiento con múltiples usuarios

**Escenario**: 5 usuarios simultáneos haciendo consultas

**Validaciones**:
- Sin degradación significativa de performance
- Sin errores de concurrencia
- Responses consistentes entre usuarios
- Sistema estable durante la prueba

---

## 🛡️ Tests de Seguridad

### TC-070: Validación de API Key
**Objetivo**: Verificar protección de endpoints

**Configuración**: API Key habilitada

**Tests**:
1. **Sin API Key**: Debe fallar con 401
2. **API Key incorrecta**: Debe fallar con 401  
3. **API Key correcta**: Debe funcionar normalmente
4. **Endpoints públicos** (/health, /docs): Deben funcionar sin key

**Criterios de Aceptación**:
- Protección efectiva de endpoints sensibles
- Mensajes de error apropiados
- No exposición de información sensible

---

### TC-071: Inyección de Datos
**Objetivo**: Validar protección contra inputs maliciosos

**Inputs de Prueba**:
```
"<script>alert('xss')</script>"
"'; DROP TABLE customers; --"  
"../../../etc/passwd"
"{{7*7}}"
```

**Criterios de Aceptación**:
- Inputs sanitizados apropiadamente
- Sin ejecución de código malicioso
- Errores de validación claros
- Sistema permanece estable

---

## 🔄 Tests de Integración

### TC-080: Workflow Completo de Ventas
**Objetivo**: Validar flujo de negocio end-to-end

**Escenario**:
1. **Buscar cliente** existente
2. **Consultar productos** disponibles  
3. **Revisar órdenes** anteriores del cliente
4. **Crear nuevo cliente** si no existe
5. **Sugerir productos** basado en historial

**Validaciones**:
- Flujo lógico mantenido
- Contexto preservado entre pasos
- Datos consistentes
- Experiencia de usuario fluida

---

### TC-081: Workflow de Gestión de Inventario
**Objetivo**: Validar flujo de consulta de inventario

**Escenario**:
1. **Consultar productos** con stock bajo
2. **Identificar clientes** que compran esos productos
3. **Revisar órdenes recientes** de esos productos
4. **Sugerir acciones** de reposición o venta

**Validaciones**:
- Análisis cruzado de datos
- Insights de negocio válidos
- Recomendaciones apropiadas
- Datos actualizados y precisos

---

## 📊 Matriz de Cobertura

| Funcionalidad | Tests Básicos | Tests Avanzados | Performance | Seguridad |
|---------------|---------------|-----------------|-------------|-----------|
| Health Check | ✅ TC-001 | - | ✅ TC-060 | - |
| Get Customers | ✅ TC-010, TC-011 | ✅ TC-050 | ✅ TC-060 | ✅ TC-070 |
| Customer Search | ✅ TC-011, TC-012 | ✅ TC-051 | ✅ TC-060 | ✅ TC-071 |
| Get Items | ✅ TC-020, TC-021 | ✅ TC-081 | ✅ TC-060 | ✅ TC-070 |
| Get Orders | ✅ TC-030 | ✅ TC-050, TC-080 | ✅ TC-060 | ✅ TC-070 |
| Create Customer | ✅ TC-040, TC-041 | ✅ TC-080 | ✅ TC-060 | ✅ TC-071 |
| Error Handling | ✅ TC-002, TC-012 | ✅ TC-051 | - | ✅ TC-070 |

---

## 🎯 Criterios de Aceptación Global

### Funcionalidad
- [ ] Todas las operaciones del conector funcionan correctamente
- [ ] Manejo apropiado de errores y casos edge
- [ ] Respuestas consistentes y bien formateadas
- [ ] Flujos conversacionales naturales

### Performance  
- [ ] Tiempos de respuesta < 10 segundos
- [ ] Comportamiento estable bajo carga
- [ ] Manejo apropiado de timeouts
- [ ] Indicadores de progreso cuando necesarios

### Usabilidad
- [ ] Interfaz conversacional intuitiva
- [ ] Mensajes de error comprensibles
- [ ] Sugerencias de seguimiento útiles
- [ ] Formateo visual apropiado

### Seguridad
- [ ] Autenticación funcionando correctamente
- [ ] Validación de inputs implementada
- [ ] No exposición de datos sensibles
- [ ] Logs de auditoría apropiados

---

## 📝 Checklist de Validación

### Pre-implementación
- [ ] Servidor MCP desplegado y operativo
- [ ] Variables de entorno configuradas
- [ ] API Key generada y configurada (si aplica)
- [ ] Documentación OpenAPI accesible

### Durante Testing
- [ ] Ejecutar todos los casos de prueba básicos
- [ ] Validar casos edge y manejo de errores
- [ ] Medir performance en condiciones normales
- [ ] Verificar seguridad y autenticación

### Post-implementación
- [ ] Documentar resultados de testing
- [ ] Configurar monitorización continua
- [ ] Establecer proceso de mantenimiento
- [ ] Capacitar usuarios finales

---

**🎉 Suite de testing completa para garantizar un conector robusto y confiable!**

Ejecuta estos casos de prueba antes de poner en producción para asegurar una experiencia óptima para tus usuarios. 🚀
