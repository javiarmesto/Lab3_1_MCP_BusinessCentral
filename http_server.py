"""
http_server.py

Servidor MCP para Microsoft Dynamics 365 Business Central usando el SDK oficial FastMCP.

Características principales:
  - Expone herramientas MCP nativas vía HTTP/ASGI (streamable y REST).
  - Soporta transporte Streamable HTTP (recomendado para producción), endpoints REST y protocolo MCP completo (SSE, JSON-RPC).
  - Métodos disponibles: get_customers, get_customer_details, get_items, get_sales_orders, create_customer.

Onboarding rápido:
  1. Configura el archivo `.env` y valida la conexión con Business Central.
  2. Ejecuta en producción: `python -m http_server`
  3. Para desarrollo/inspección: `uv run mcp dev http_server.py`
  4. Consulta los docstrings de cada herramienta para ejemplos y detalles de uso.

Referencias útiles:
  - FastMCP deployment: https://gofastmcp.com/deployment/asgi
  - APIs REST de Business Central: https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/api-overview
  - Blog TechSphereDynamics: https://techspheredynamics.com
"""
from typing import Optional
import os
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv

# Cargar variables de entorno
project_root = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

# SDK oficial MCP
#from mcp.server.fastmcp import FastMCP, Context
from config import config
from client import bc_client
from fastmcp import FastMCP, Context

# Configuración global de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("http_server")


@dataclass
class AppContext:
    """
    Contexto de la aplicación para el ciclo de vida del servidor MCP.
    Permite inicialización y limpieza de recursos globales.
    """
    initialized: bool = False


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """
    Gestión del ciclo de vida del servidor MCP (startup/shutdown).
    Valida configuración y permite inicialización de recursos globales.
    """
    logger.info("Iniciando servidor MCP Business Central...")
    # Validar configuración al inicio
    if not config.validate():
        logger.error("Configuración inválida - revisar variables de entorno")
        raise RuntimeError("Configuración inválida")
    logger.info("Configuración validada correctamente")
    try:
        yield AppContext(initialized=True)
    finally:
        logger.info("Cerrando servidor MCP Business Central...")



# Crear servidor MCP usando SDK oficial
mcp = FastMCP(
    name="BusinessCentral",
    lifespan=app_lifespan,
    stateless_http=True,  # Sin persistencia de sesión
    dependencies=["httpx", "pydantic", "python-dotenv"]
)


logger.info("Servidor MCP Business Central inicializado con SDK oficial")
# =============================================================================
# EXPOSICIÓN ASGI PARA UVICORN - VERSIÓN OFICIAL
# =============================================================================

# Según la documentación oficial de FastMCP:
# https://gofastmcp.com/deployment/asgi
# Para deployment simple podemos usar mcp.run(transport="http") directamente
# O para ASGI personalizado, usar mcp.http_app()

# Exponer la aplicación ASGI usando el método oficial http_app()
app = mcp.http_app()
#app=mcp.streamable_http_app()
# =============================================================================
# HERRAMIENTAS MCP USANDO SDK OFICIAL
# =============================================================================


@mcp.tool()
async def get_customers(limit: int = 10) -> list[dict]:
    """
    Lista clientes de Business Central.
    Parámetros:
        limit (int): Número máximo de clientes a retornar (1-100)
    Retorna:
        Lista de clientes con información básica.
    """
    if limit < 1 or limit > 100:
        raise ValueError("El límite debe estar entre 1 y 100")
    logger.info(f"Obteniendo {limit} clientes de Business Central")
    data = await bc_client.get_customers(top=limit)
    logger.info(f"Clientes obtenidos: {len(data)}")
    return data


@mcp.tool()
async def get_customer_details(customer_id: str) -> dict:
    """
    Obtiene detalles completos de un cliente específico.
    Parámetros:
        customer_id (str): ID único del cliente en Business Central
    Retorna:
        Información detallada del cliente.
    """
    logger.info(f"Obteniendo detalles del cliente: {customer_id}")
    result = await bc_client.get_customer(customer_id)
    if not result:
        raise ValueError(f"Cliente {customer_id} no encontrado")
    return result


@mcp.tool()
async def get_items(limit: int = 10) -> list[dict]:
    """
    Lista artículos/productos disponibles en Business Central.
    Parámetros:
        limit (int): Número máximo de artículos a retornar (1-100)
    Retorna:
        Lista de artículos con información básica.
    """
    if limit < 1 or limit > 100:
        raise ValueError("El límite debe estar entre 1 y 100")
    logger.info(f"Obteniendo {limit} artículos de Business Central")
    data = await bc_client.get_items(top=limit)
    logger.info(f"Artículos obtenidos: {len(data)}")
    return data


@mcp.tool()
async def get_sales_orders(limit: int = 5) -> list[dict]:
    """
    Lista órdenes de venta de Business Central.
    Parámetros:
        limit (int): Número máximo de órdenes a retornar (1-100)
    Retorna:
        Lista de órdenes de venta.
    """
    if limit < 1 or limit > 100:
        raise ValueError("El límite debe estar entre 1 y 100")
    logger.info(f"Obteniendo {limit} órdenes de venta de Business Central")
    data = await bc_client.get_orders(top=limit)
    logger.info(f"Órdenes obtenidas: {len(data)}")
    return data


@mcp.tool()
async def create_customer(
    displayName: str,
    email: str,
    phoneNumber: Optional[str] = None,
    addressLine1: Optional[str] = None,
    city: Optional[str] = None,
    country: Optional[str] = None,
    taxRegistrationNumber: Optional[str] = None,
    ctx: Context = None
) -> dict:
    """
    Crea un nuevo cliente en Business Central.
    Parámetros:
        displayName (str): Nombre del cliente (obligatorio)
        email (str): Correo electrónico (obligatorio)
        phoneNumber (str): Número de teléfono (opcional)
        addressLine1 (str): Dirección principal (opcional)
        city (str): Ciudad (opcional)
        country (str): País (código de 2 letras, ej: ES, US) (opcional)
        taxRegistrationNumber (str): Número de identificación fiscal (opcional)
    Retorna:
        Información del cliente creado.
    """
    if not displayName or not email:
        raise ValueError("Los campos 'displayName' y 'email' son obligatorios")
    if ctx:
        await ctx.info(f"Creando cliente: {displayName}")
    logger.info(f"Creando cliente: {displayName} ({email})")
    # Preparar payload para Business Central
    customer_payload = {
        "displayName": displayName,
        "email": email,
        "phoneNumber": phoneNumber,
        "taxRegistrationNumber": taxRegistrationNumber
    }
    # Añadir dirección si se proporciona
    if addressLine1 or city or country:
        customer_payload["address"] = {}
        if addressLine1:
            customer_payload["address"]["street"] = addressLine1
        if city:
            customer_payload["address"]["city"] = city
        if country:
            customer_payload["address"]["countryLetterCode"] = country
    # Limpiar campos None
    customer_payload = {k: v for k, v in customer_payload.items() if v is not None}
    if customer_payload.get("address"):
        customer_payload["address"] = {k: v for k, v in customer_payload["address"].items() if v is not None}
        if not customer_payload["address"]:
            del customer_payload["address"]
    created_customer = await bc_client.create_customer(customer_payload)
    if ctx:
        await ctx.info(f"Cliente creado exitosamente: {created_customer.get('number', 'N/A')}")
    logger.info(f"Cliente creado: {created_customer.get('number', 'N/A')}")
    return created_customer




# =============================================================================
# EJECUCIÓN DEL SERVIDOR
# =============================================================================

if __name__ == "__main__":
    logger.info("Iniciando servidor MCP Business Central...")
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        
    )
