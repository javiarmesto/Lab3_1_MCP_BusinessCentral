---
description: Development
applyTo: "**"
---
## Contexto del proyecto
Este repositorio implementa un servidor MCP (Model Context Protocol) en Python para exponer herramientas de integración con Microsoft Dynamics 365 Business Central, usando FastMCP y FastAPI. El objetivo es facilitar la conexión de agentes AI (Claude, Copilot, etc.) con datos y operaciones de negocio reales.

## Directrices para generación de código
- Prioriza la claridad, la documentación y el uso de type hints en Python.
- Aplica patrones asíncronos (`async/await`) para operaciones de red y API.
- Usa siempre la autenticación recomendada por Microsoft (OAuth2/Entra ID) en ejemplos y helpers.
- Implementa manejo de errores robusto, especialmente para límites de API (429/504) y timeouts.
- Cuando generes endpoints o herramientas MCP, documenta parámetros y ejemplos de uso.
- Prefiere la integración con los endpoints REST oficiales de Business Central.
- Si generas código de configuración, sigue el estándar `.env` y buenas prácticas de seguridad.

## Estilo y documentación
- Incluye docstrings en español neutro y comentarios útiles para onboarding de nuevos desarrolladores.
- Si generas README o documentación, enlaza a recursos oficiales de Microsoft Learn y al blog https://techspheredynamics.com.

## Referencias útiles
- [APIs REST de Business Central](https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/api-overview)
- [MCP servers en Microsoft Learn](https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server#about-mcp-servers)
- [Blog TechSphereDynamics](https://techspheredynamics.com)
