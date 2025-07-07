"""
mcp_stm_server.py

Servidor MCP Business Central (versión STM) usando el SDK oficial de MCP Python con FastMCP.
Expone las mismas herramientas que http_server.py, pero sigue la plantilla recomendada para servidores STM.
Incluye el endpoint listtools.

Uso en producción:
  python -m mcp_stm_server

Desarrollo con inspector MCP:
  uv run mcp dev mcp_stm_server.py
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
from mcp.server.fastmcp import FastMCP, Context
from config import config
from client import bc_client

# Configuración global de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("mcp_stm_server")

@dataclass
class AppContext:
    """Contexto de la aplicación para el ciclo de vida del servidor"""
    initialized: bool = False

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Gestión del ciclo de vida del servidor MCP"""
    logger.info("Iniciando servidor MCP Business Central (STM)...")
    if not config.validate():
        logger.error("Configuración inválida - revisar variables de entorno")
        raise RuntimeError("Configuración inválida")
    logger.info("Configuración validada correctamente")
    try:
        yield AppContext(initialized=True)
    finally:
        logger.info("Cerrando servidor MCP Business Central (STM)...")

# Crear servidor MCP STM
mcp = FastMCP(
    name="BusinessCentralSTM",
    lifespan=app_lifespan,
    stateless_http=True,
    dependencies=["httpx", "pydantic", "python-dotenv"]
)

logger.info("Servidor MCP Business Central STM inicializado con SDK oficial")

# =============================================================================
# HERRAMIENTAS MCP USANDO SDK OFICIAL (idénticas a http_server)
# =============================================================================

@mcp.tool()
async def get_customers(limit: int = 10) -> list[dict]:
    """
    Lista clientes de Business Central.
    Args:
        limit: Número máximo de clientes a retornar (1-100)
    Returns:
        Lista de clientes con información básica
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
    Args:
        customer_id: ID único del cliente en Business Central
    Returns:
        Información detallada del cliente
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
    Args:
        limit: Número máximo de artículos a retornar (1-100)
    Returns:
        Lista de artículos con información básica
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
    Args:
        limit: Número máximo de órdenes a retornar (1-100)
    Returns:
        Lista de órdenes de venta
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
    Args:
        displayName: Nombre del cliente (obligatorio)
        email: Correo electrónico (obligatorio)
        phoneNumber: Número de teléfono (opcional)
        addressLine1: Dirección principal (opcional)
        city: Ciudad (opcional)
        country: País (código de 2 letras, ej: ES, US) (opcional)
        taxRegistrationNumber: Número de identificación fiscal (opcional)
    Returns:
        Información del cliente creado
    """
    if not displayName or not email:
        raise ValueError("Los campos 'displayName' y 'email' son obligatorios")
    if ctx:
        await ctx.info(f"Creando cliente: {displayName}")
    logger.info(f"Creando cliente: {displayName} ({email})")
    customer_payload = {
        "displayName": displayName,
        "email": email,
        "phoneNumber": phoneNumber,
        "taxRegistrationNumber": taxRegistrationNumber
    }
    if addressLine1 or city or country:
        customer_payload["address"] = {}
        if addressLine1:
            customer_payload["address"]["street"] = addressLine1
        if city:
            customer_payload["address"]["city"] = city
        if country:
            customer_payload["address"]["countryLetterCode"] = country
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

# Endpoint especial: listtools
@mcp.tool()
async def listtools() -> list[str]:
    """
    Devuelve la lista de herramientas MCP expuestas por el servidor.
    Returns:
        Lista de nombres de herramientas
    """
    return [tool.name for tool in mcp.tools]

# =============================================================================
# EJECUCIÓN DEL SERVIDOR
# =============================================================================

def main():
    """Punto de entrada principal del servidor MCP STM"""
    logger.info("Iniciando servidor MCP Business Central STM...")
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
