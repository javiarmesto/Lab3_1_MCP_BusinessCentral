"""
http_server.py

Servidor MCP Business Central usando el SDK oficial de MCP Python con FastMCP.
Expone herramientas MCP nativas con soporte para:
  - Transporte Streamable HTTP (recomendado para producción)
  - Endpoints REST tradicionales para compatibilidad
  - Protocolo MCP completo con SSE y JSON-RPC

Capacidades:
  - get_customers: Lista clientes de Business Central
  - get_customer_details: Detalle de un cliente por ID  
  - get_items: Lista artículos/productos
  - get_sales_orders: Lista órdenes de venta
  - create_customer: Crea nuevos clientes

Uso en producción:
  python -m bc_server.http_server
  
Desarrollo con inspector MCP:
  uv run mcp dev bc_server/http_server.py
"""
from typing import Optional
import os
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator
from dataclasses import dataclass
from dotenv import load_dotenv

# Cargar variables de entorno
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

# SDK oficial MCP
from mcp.server.fastmcp import FastMCP, Context
from bc_server_bkp.config import config
from bc_server_bkp.client import bc_client

# Configuración global de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("http_server")

@dataclass
class AppContext:
    """Contexto de la aplicación para el ciclo de vida del servidor"""
    initialized: bool = False

@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Gestión del ciclo de vida del servidor MCP"""
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
    # Configuración para Streamable HTTP (recomendado para producción)
    stateless_http=True,  # Sin persistencia de sesión
    dependencies=["httpx", "pydantic", "python-dotenv"]  # Para deployment automático
)

logger.info("Servidor MCP Business Central inicializado con SDK oficial")

# =============================================================================
# HERRAMIENTAS MCP USANDO SDK OFICIAL
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

def main():
    """Punto de entrada principal del servidor MCP"""
    logger.info("Iniciando servidor MCP Business Central...")
    
    # Ejecutar con transporte Streamable HTTP (recomendado para producción)
    # Esto expone automáticamente el endpoint /mcp para JSON-RPC
    mcp.run(transport="streamable-http")

if __name__ == "__main__":
    main()
