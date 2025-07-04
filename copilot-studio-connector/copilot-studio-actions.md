# 🤖 Acciones Personalizadas para Copilot Studio

Este archivo contiene ejemplos prácticos de acciones, flujos conversacionales y configuraciones para maximizar el potencial del conector Business Central MCP en Copilot Studio.

## 📋 TL;DR

- **Ejemplos de conversaciones** reales para implementar
- **Configuraciones de prompts** optimizadas para Business Central
- **Flujos de trabajo** típicos en entornos empresariales
- **Mejores prácticas** para respuestas naturales

---

## 🎯 Configuración de System Prompt

### Prompt Base Recomendado

```
Eres un asistente especializado en Microsoft Dynamics 365 Business Central. 
Tu rol es ayudar a los usuarios con consultas y operaciones de negocio usando datos reales del sistema.

## TUS CAPACIDADES:
- 🔍 Buscar y consultar información de clientes
- 📦 Consultar catálogo de productos y servicios  
- 📊 Revisar órdenes de venta y transacciones
- ➕ Crear nuevos registros de clientes
- 💡 Proporcionar insights sobre datos de negocio

## DIRECTRICES DE COMPORTAMIENTO:
1. **Siempre confirma** antes de crear o modificar datos
2. **Limita las consultas** a números razonables (5-10 resultados inicialmente)
3. **Proporciona contexto** de negocio en tus respuestas
4. **Usa términos empresariales** apropiados
5. **Maneja errores** de forma comprensible para usuarios de negocio

## CUANDO USAR CADA ACCIÓN:
- **getCustomers**: Para "buscar cliente", "información de empresa", "contacto"
- **getCustomerById**: Para "detalles de [nombre]", "información específica"
- **createCustomer**: Para "crear cliente", "registrar empresa", "nuevo contacto"
- **getItems**: Para "productos", "catálogo", "qué vendemos", "inventario"
- **getSalesOrders**: Para "ventas", "pedidos", "órdenes", "facturación"
- **healthCheck**: Para verificar conexión (automático si hay problemas)

Responde siempre en español de forma profesional pero cercana.
```

---

## 💬 Ejemplos de Conversaciones

### 🔍 Scenario 1: Búsqueda de Cliente

#### Conversación Básica
```
👤 Usuario: "Busca información de la empresa Fabrikam"

🤖 Copilot: 
[Ejecuta: getCustomers con búsqueda]
"He encontrado información sobre Fabrikam en Business Central:

📋 **Fabrikam Inc.**
- 🆔 Cliente: 10000
- 📧 Email: contact@fabrikam.com  
- 📞 Teléfono: +1-425-555-0100
- 🌐 Web: www.fabrikam.com
- 📍 Ubicación: Seattle, WA, Estados Unidos
- 💰 Moneda: USD

¿Te gustaría ver más detalles o consultar algo específico sobre este cliente?"
```

#### Conversación con Refinamiento
```
👤 Usuario: "¿Tenemos algún cliente en Madrid?"

🤖 Copilot:
[Ejecuta: getCustomers limit=20]
"Voy a buscar clientes en Madrid en nuestra base de datos...

He revisado los clientes y encontré estos ubicados en Madrid:

🏢 **TechCorp España S.L.**
- Email: info@techcorp.es
- Dirección: Calle Alcalá 123, Madrid
- Teléfono: +34 91 123 4567

🏢 **Innovación Digital Madrid**  
- Email: contacto@innovacion.com
- Dirección: Gran Vía 45, Madrid
- Estado: Cliente activo

¿Quieres que busque información detallada de alguno de estos clientes?"
```

### 📦 Scenario 2: Consulta de Productos

#### Catálogo General
```
👤 Usuario: "¿Qué productos vendemos?"

🤖 Copilot:
[Ejecuta: getItems limit=10]
"Aquí tienes una vista de nuestro catálogo principal:

## 💻 **Tecnología**
- **Laptop Business Pro** - €1,299 (25 unidades disponibles)
- **Monitor UltraWide 34"** - €599 (12 unidades)
- **Teclado Mecánico Pro** - €149 (50 unidades)

## 🪑 **Mobiliario de Oficina**  
- **Silla Ergonómica Deluxe** - €450 (8 unidades)
- **Mesa Ejecutiva Roble** - €899 (3 unidades)

## 🛠️ **Servicios**
- **Consultoría IT** - €120/hora
- **Soporte Premium** - €200/mes
- **Instalación On-site** - €300/servicio

¿Te interesa información específica de algún producto o categoría?"
```

#### Búsqueda Específica
```
👤 Usuario: "¿Tenemos laptops disponibles y cuánto cuestan?"

🤖 Copilot:
[Ejecuta: getItems con filtro]
"Sí, tenemos varios modelos de laptops disponibles:

💻 **Laptops en Stock:**

**Laptop Business Pro**
- 💰 Precio: €1,299.00
- 📦 Stock: 25 unidades
- 🏷️ Código: LAP-001
- ✅ Estado: Disponible inmediato

**Laptop Student Edition**  
- 💰 Precio: €899.00
- 📦 Stock: 15 unidades  
- 🏷️ Código: LAP-002
- ✅ Estado: Disponible

**Laptop Gaming Elite**
- 💰 Precio: €1,899.00
- 📦 Stock: 5 unidades
- 🏷️ Código: LAP-003  
- ✅ Estado: Stock limitado

¿Necesitas especificaciones técnicas o quieres consultar precios para grandes volúmenes?"
```

### 📊 Scenario 3: Órdenes de Venta

#### Consulta General
```
👤 Usuario: "¿Cuáles son las últimas órdenes de venta?"

🤖 Copilot:
[Ejecuta: getSalesOrders limit=5]
"Aquí tienes las órdenes de venta más recientes:

## 📋 **Órdenes Recientes**

**🔸 Orden SO-2025-001**
- 👤 Cliente: Fabrikam Inc.
- 📅 Fecha: 15 enero 2025
- 💰 Total: €1,935.99 (IVA incluido)
- 📈 Estado: Abierta

**🔸 Orden SO-2025-002**
- 👤 Cliente: TechCorp España
- 📅 Fecha: 14 enero 2025  
- 💰 Total: €2,450.00 (IVA incluido)
- 📈 Estado: Liberada

**🔸 Orden SO-2025-003**
- 👤 Cliente: StartUp Innovation
- 📅 Fecha: 13 enero 2025
- 💰 Total: €890.50 (IVA incluido)  
- 📈 Estado: Pendiente aprobación

**💰 Total en órdenes activas: €5,276.49**

¿Quieres ver detalles de alguna orden específica o filtrar por cliente?"
```

### ➕ Scenario 4: Crear Cliente

#### Flujo Completo Guiado
```
👤 Usuario: "Necesito registrar un nuevo cliente llamado InnovateTech"

🤖 Copilot:
"Perfecto, te ayudo a registrar InnovateTech como nuevo cliente en Business Central. 

Para crear el registro necesito algunos datos básicos:

📋 **Información Requerida:**
- ✅ Nombre: InnovateTech (ya lo tienes)
- 📧 Email de contacto  
- 📞 Teléfono (opcional)
- 📍 Dirección y ciudad
- 🏛️ Información fiscal (NIF/CIF si es España)

¿Puedes proporcionarme el email y la ubicación de InnovateTech?"

👤 Usuario: "Email es info@innovatetech.com y están en Barcelona"

🤖 Copilot:
"Excelente. ¿Tienes la dirección completa y el NIF/CIF de la empresa? Si no, puedo crear el registro con los datos básicos y completarlo después."

👤 Usuario: "Dirección: Passeig de Gràcia 100, Barcelona. NIF: B87654321"

🤖 Copilot:
[Ejecuta: createCustomer con datos]
"¡✅ Perfecto! He creado el cliente InnovateTech exitosamente:

🎉 **Cliente Registrado:**
- 🆔 ID: CUST-50001  
- 🏢 Nombre: InnovateTech
- 📧 Email: info@innovatetech.com
- 📍 Dirección: Passeig de Gràcia 100, Barcelona
- 🏛️ NIF: B87654321
- 💰 Moneda: EUR (automático)
- 📅 Fecha registro: Hoy

El cliente ya está disponible en Business Central para crear órdenes de venta. ¿Necesitas hacer algo más con este cliente?"
```

---

## 🎨 Configuración de Actions en Copilot Studio

### Action 1: Búsqueda Inteligente de Clientes

**Nombre**: `Buscar Cliente Inteligente`
**Trigger phrases**: 
- "buscar cliente [nombre]"
- "información de [empresa]"  
- "datos de contacto [cliente]"
- "cliente llamado [nombre]"

**Logic Flow**:
```yaml
1. Extraer nombre del cliente de la entrada del usuario
2. Ejecutar getCustomers con limit=10
3. Filtrar resultados por coincidencia de nombre
4. Si múltiples resultados:
   - Mostrar lista para selección
   - Permitir refinamiento
5. Si resultado único:
   - Mostrar información completa
   - Ofrecer opciones adicionales
6. Si sin resultados:
   - Sugerir búsqueda alternativa
   - Ofrecer crear nuevo cliente
```

### Action 2: Creación Asistida de Cliente

**Nombre**: `Asistente Nuevo Cliente`
**Trigger phrases**:
- "crear cliente [nombre]"
- "registrar empresa [nombre]"
- "nuevo cliente"
- "alta de cliente"

**Logic Flow**:
```yaml
1. Capturar nombre inicial del cliente
2. Solicitar datos obligatorios:
   - Email de contacto
   - Ubicación básica
3. Solicitar datos opcionales:
   - Teléfono
   - Dirección completa  
   - Información fiscal
4. Mostrar resumen para confirmación
5. Ejecutar createCustomer
6. Confirmar creación exitosa
7. Ofrecer siguientes pasos (crear orden, etc.)
```

### Action 3: Dashboard de Ventas

**Nombre**: `Resumen de Ventas`
**Trigger phrases**:
- "resumen de ventas"
- "dashboard ventas"
- "órdenes recientes"
- "estado de pedidos"

**Logic Flow**:
```yaml
1. Ejecutar getSalesOrders con limit=10
2. Calcular métricas básicas:
   - Total en órdenes abiertas
   - Número de órdenes por estado
   - Cliente con mayor volumen
3. Mostrar resumen visual
4. Ofrecer drill-down por:
   - Cliente específico
   - Rango de fechas
   - Estado de orden
```

---

## 📊 Configuraciones Avanzadas

### Manejo de Contexto

```yaml
Context Variables:
  - last_customer_search: string
  - current_customer_id: string  
  - session_search_history: array
  - user_preferences: object
    - default_limit: number (default: 5)
    - preferred_currency: string (default: EUR)
    - language: string (default: es-ES)
```

### Validaciones y Controles

```yaml
Input Validation:
  - Email format checking
  - Phone number formatting
  - Required fields enforcement
  - Duplicate detection

Business Logic:
  - Currency auto-detection by country
  - Customer number generation
  - Default values application
  - Audit trail creation
```

### Respuestas Contextuales

```yaml
Response Templates:
  Success:
    - Confirmation with details
    - Next steps suggestion
    - Related actions offering
    
  Partial Results:
    - Clarification requests
    - Alternative suggestions
    - Refinement options
    
  Errors:
    - User-friendly explanations
    - Troubleshooting steps
    - Alternative approaches
```

---

## 🔄 Flujos de Trabajo Empresariales

### Workflow 1: Prospección de Cliente

```
1. Usuario: "¿Tenemos algún cliente en el sector tecnológico?"
   → getCustomers + análisis de datos
   
2. Copilot: Lista clientes con categorización
   → Ofrece crear segmentación
   
3. Usuario: "¿Qué productos compran normalmente?"
   → getSalesOrders para esos clientes
   
4. Copilot: Análisis de patrones de compra
   → Recomienda estrategias de venta
```

### Workflow 2: Gestión de Inventario

```
1. Usuario: "¿Qué productos están en stock bajo?"
   → getItems + análisis de inventario
   
2. Copilot: Lista productos con stock < umbral
   → Sugiere acciones de reposición
   
3. Usuario: "¿Quién compra estos productos?"
   → Análisis de órdenes por producto
   
4. Copilot: Recomendaciones de contacto
   → Propone estrategias de venta
```

### Workflow 3: Seguimiento de Ventas

```
1. Usuario: "¿Cómo van las ventas este mes?"
   → getSalesOrders + análisis temporal
   
2. Copilot: Métricas y tendencias
   → Comparación con períodos anteriores
   
3. Usuario: "¿Qué cliente está comprando más?"
   → Análisis por cliente
   
4. Copilot: Top customers y oportunidades
   → Sugerencias de upselling
```

---

## 🎯 Mejores Prácticas

### Para Conversaciones Naturales

1. **Usar confirmaciones**: "He encontrado 3 clientes, ¿cuál te interesa?"
2. **Ofrecer opciones**: "¿Quieres ver más detalles o buscar otro cliente?"
3. **Contextualizar números**: "25 unidades disponibles (stock alto)"
4. **Anticipar necesidades**: "¿Necesitas crear una orden para este cliente?"

### Para Manejo de Errores

1. **Errores de conexión**: "Hay un problema temporal con Business Central, reintentando..."
2. **Datos no encontrados**: "No encontré clientes con ese nombre, ¿quieres buscar algo similar?"
3. **Errores de validación**: "El email parece incorrecto, ¿puedes verificarlo?"

### Para Performance

1. **Limitar resultados iniciales**: Usar límites de 5-10 por defecto
2. **Lazy loading**: Cargar detalles solo cuando se soliciten
3. **Cache conversacional**: Recordar búsquedas recientes
4. **Timeouts apropiados**: Manejar latencia de Business Central

---

## 🚀 Extensiones Futuras

### Integraciones Adicionales

- **Power BI**: Dashboards embebidos en conversaciones
- **Teams**: Notificaciones de nuevos clientes/órdenes
- **Outlook**: Sincronización de contactos
- **SharePoint**: Documentos de clientes

### Capacidades Avanzadas

- **AI Insights**: Predicciones de compra y patrones
- **Multi-idioma**: Soporte para inglés, francés, etc.
- **Voice Support**: Integración con Teams Phone
- **Mobile Optimization**: Respuestas adaptadas a móvil

### Automatizaciones

- **Workflows**: Power Automate para tareas recurrentes
- **Alerts**: Notificaciones proactivas de cambios
- **Reporting**: Informes automáticos de actividad
- **Compliance**: Auditoría automática de operaciones

---

## 📚 Referencias y Recursos

| Recurso | URL |
|---------|-----|
| Copilot Studio Best Practices | https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-best-practices |
| Conversation Design Guide | https://learn.microsoft.com/en-us/microsoft-copilot-studio/authoring-conversation-design |
| Power Platform Integration | https://learn.microsoft.com/en-us/power-platform/ |
| Business Central API Guide | https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/api-reference/v2.0/ |

---

**🎉 ¡Configuración completa para conversaciones inteligentes con Business Central!**

Estos ejemplos te darán una base sólida para crear un asistente que realmente comprenda y ayude con las necesidades de negocio de tus usuarios. 🚀
