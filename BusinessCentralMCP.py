"""
BusinessCentralMCP.py

Servidor MCP (JSON-RPC) para Microsoft Dynamics 365 Business Central usando FastMCP.

Exposición de herramientas MCP para integración con agentes AI (Claude, Copilot, etc.):
  - get_customers(limit: int): Lista clientes de BC
  - get_customer_details(customer_id: str): Detalle de un cliente
  - get_items(limit: int): Lista artículos
  - get_sales_orders(limit: int): Lista órdenes de venta
  - create_customer(...): Crea un nuevo cliente

Este servidor:
  - Lee configuración desde `.env` (según buenas prácticas de seguridad)
  - Valida credenciales y entorno
  - Expone métodos MCP vía FastMCP para integración con clientes AI

Onboarding rápido:
  1. Configura el archivo `.env` con los parámetros de autenticación y endpoint de Business Central.
  2. Ejecuta: `python -m BusinessCentralMCP` para modo CLI/JSON-RPC, o usa el servidor ASGI para despliegue web.
  3. Consulta la documentación de cada herramienta en los docstrings o en el README.

Referencias útiles:
  - APIs REST de Business Central: https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/api-overview
  - MCP servers en Microsoft Learn: https://learn.microsoft.com/en-us/azure/api-management/export-rest-mcp-server#about-mcp-servers
  - Blog TechSphereDynamics: https://techspheredynamics.com
"""

import os
import sys
import asyncio
import getpass
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, Optional


# Cargar variables de entorno desde .env en la raíz del proyecto
project_root = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

# Asegurar importaciones desde el paquete raíz
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp.server.fastmcp import FastMCP
from config import config
from client import bc_client


# Inicializar servidor MCP para Business Central
mcp = FastMCP("BusinessCentral")

# COMENTAMOS LA FUNCIÓN LIST_TOOLS PARA EVITAR CONFLICTOS
# @mcp.method("tools/list")
# async def list_tools():
#     """
#     Devuelve la lista de herramientas MCP disponibles para discovery automático.
#     Incluye inputSchema para compatibilidad con Copilot Studio.
#     """
#     return {
#         "tools": [
#             {
#                 "name": "get_customers", 
#                 "description": "Lista clientes de Business Central",
#                 "inputSchema": {
#                     "type": "object",
#                     "properties": {
#                         "limit": {
#                             "type": "integer",
#                             "description": "Número máximo de clientes a retornar",
#                             "default": 10
#                         }
#                     }
#                 }
#             },
#             {
#                 "name": "get_customer_details", 
#                 "description": "Muestra detalles de un cliente por ID",
#                 "inputSchema": {
#                     "type": "object",
#                     "properties": {
#                         "customer_id": {
#                             "type": "string",
#                             "description": "ID único del cliente en Business Central"
#                         }
#                     },
#                     "required": ["customer_id"]
#                 }
#             },
#             {
#                 "name": "get_items", 
#                 "description": "Lista artículos de Business Central",
#                 "inputSchema": {
#                     "type": "object",
#                     "properties": {
#                         "limit": {
#                             "type": "integer",
#                             "description": "Número máximo de artículos a retornar",
#                             "default": 10
#                         }
#                     }
#                 }
#             },
#             {
#                 "name": "get_sales_orders", 
#                 "description": "Lista órdenes de venta de Business Central",
#                 "inputSchema": {
#                     "type": "object",
#                     "properties": {
#                         "limit": {
#                             "type": "integer",
#                             "description": "Número máximo de órdenes a retornar",
#                             "default": 5
#                         }
#                     }
#                 }
#             },
#             {
#                 "name": "create_customer", 
#                 "description": "Crea un nuevo cliente en Business Central",
#                 "inputSchema": {
#                     "type": "object",
#                     "properties": {
#                         "displayName": {
#                             "type": "string",
#                             "description": "Nombre del cliente"
#                         },
#                         "type": {
#                             "type": "string",
#                             "description": "Tipo de cliente",
#                             "default": "Company"
#                         },
#                         "addressLine1": {
#                             "type": "string",
#                             "description": "Dirección principal"
#                         },
#                         "city": {
#                             "type": "string",
#                             "description": "Ciudad"
#                         },
#                         "email": {
#                             "type": "string",
#                             "description": "Correo electrónico"
#                         },
#                         "phoneNumber": {
#                             "type": "string",
#                             "description": "Número de teléfono"
#                         }
#                     },
#                     "required": ["displayName"]
#                 }
#             }
#         ]
#     }


@mcp.tool()
async def get_customers(limit: int = 10):
    """
    Lista clientes de Business Central.
    Parámetros:
        limit (int): Número máximo de clientes a retornar (por defecto 10).
    Retorna:
        Lista de clientes o error de configuración.
    """
    if not config.validate():
        return {"error": "configuración inválida"}
    return await bc_client.get_customers(top=limit)


@mcp.tool()
async def get_customer_details(customer_id: str):
    """
    Muestra detalles de un cliente por ID.
    Parámetros:
        customer_id (str): ID único del cliente en Business Central.
    Retorna:
        Detalles del cliente o error si no se encuentra.
    """
    if not config.validate():
        return {"error": "configuración inválida"}
    result = await bc_client.get_customer(customer_id)
    return result or {"error": "cliente no encontrado"}


@mcp.tool()
async def get_items(limit: int = 10):
    """
    Lista artículos de Business Central.
    Parámetros:
        limit (int): Número máximo de artículos a retornar (por defecto 10).
    Retorna:
        Lista de artículos o error de configuración.
    """
    if not config.validate():
        return {"error": "configuración inválida"}
    return await bc_client.get_items(top=limit)


@mcp.tool()
async def get_sales_orders(limit: int = 5):
    """
    Lista órdenes de venta de Business Central.
    Parámetros:
        limit (int): Número máximo de órdenes a retornar (por defecto 5).
    Retorna:
        Lista de órdenes de venta o error de configuración.
    """
    if not config.validate():
        return {"error": "configuración inválida"}
    return await bc_client.get_orders(top=limit)


@mcp.tool(name="create_customer")
async def create_customer(
    displayName: str,
    type: str = "Company",
    addressLine1: str = "",
    addressLine2: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    country: Optional[str] = None,
    postalCode: Optional[str] = None,
    phoneNumber: Optional[str] = None,
    email: Optional[str] = None,
    website: Optional[str] = None,
    taxLiable: bool = True,
    taxAreaId: Optional[str] = None,
    taxRegistrationNumber: Optional[str] = None,
    currencyId: Optional[str] = None,
    currencyCode: Optional[str] = None,
    paymentTermsId: Optional[str] = None,
    shipmentMethodId: Optional[str] = None,
    paymentMethodId: Optional[str] = None,
    blocked: Optional[str] = None
) -> Dict[str, Any]:
    """
    Crea un nuevo cliente en Business Central.
    Parámetros principales:
        displayName (str): Nombre del cliente (obligatorio)
        email (str): Correo electrónico (obligatorio)
        type (str): Tipo de cliente (por defecto 'Company')
        addressLine1, addressLine2, city, state, country, postalCode, phoneNumber, website, etc.
        taxRegistrationNumber (str): Recomendado para clientes fiscales
    Retorna:
        Resultado de la creación o advertencia/error.
    Notas:
        - Todos los parámetros corresponden a los campos de la entidad Customer de BC.
        - Se recomienda proporcionar 'taxRegistrationNumber' para clientes fiscales.
    """
    # Validación de campos obligatorios
    if not displayName or not email:
        return {"error": "Los campos 'displayName' y 'email' son obligatorios"}
    # Recomendación de incluir taxRegistrationNumber
    if not taxRegistrationNumber:
        # Se puede optar por un warning o log, aquí devolvemos advertencia
        return {"warning": "Es recomendable proporcionar 'taxRegistrationNumber'"}
    customer_data: Dict[str, Any] = {
        "displayName": displayName,
        "type": type,
        "addressLine1": addressLine1,
        "addressLine2": addressLine2,
        "city": city,
        "state": state,
        "country": country,
        "postalCode": postalCode,
        "phoneNumber": phoneNumber,
        "email": email,
        "website": website,
        "taxLiable": taxLiable,
        "taxAreaId": taxAreaId,
        "taxRegistrationNumber": taxRegistrationNumber,
        "currencyId": currencyId,
        "currencyCode": currencyCode,
        "paymentTermsId": paymentTermsId,
        "shipmentMethodId": shipmentMethodId,
        "paymentMethodId": paymentMethodId,
        "blocked": blocked
    }
    return await bc_client.create_customer(customer_data)


if __name__ == "__main__":
    # Mensaje de bienvenida y contexto de ejecución
    usuario = getpass.getuser()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"""
🚀 Servidor MCP BusinessCentral listo y esperando comandos... | Circe & Javier Armesto Powered 🤖✨
👤 Usuario: {usuario} | 🕒 Inicio: {fecha}
💡 Tip Circe: Usa get_customers(limit) para listar clientes rápidamente.
---------------------------------------------------------------
""")
    mcp.run()
