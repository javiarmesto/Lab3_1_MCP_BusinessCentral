# bc_server package
"""
El paquete bc_server contiene la implementación de varias herramientas y servicios
para interactuar con Microsoft Business Central a través de MCP y HTTP:
  1. BusinessCentralMCP.py - Servidor MCP (JSON-RPC) para BC
  2. http_server.py - API REST (FastAPI) con endpoints OpenAPI/Swagger
  3. setup_guide.py - Script formativo para validar entorno y credenciales
  4. client.py - Cliente HTTP resiliente para la API de BC
  5. config.py - Carga y validación de configuración (Azure AD, BC)
"""
# Version del paquete
__version__ = "0.1.0"
