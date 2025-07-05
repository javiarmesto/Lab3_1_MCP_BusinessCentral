"""
BusinessCentralMCP.py

Servidor MCP (JSON-RPC) para Microsoft Business Central usando FastMCP.
Exponer herramientas que permiten a Claude o Copilot invocar operaciones en BC:
  - get_customers(limit: int)            Lista clientes de BC
  - get_customer_details(customer_id: str)    Detalle de un cliente
  - get_items(limit: int)                 Lista artículos
  - get_sales_orders(limit: int)          Lista órdenes de venta

Este servidor lee configuración de `.env`, valida credenciales y ejecuta
un bucle JSON-RPC sobre stdin/stdout para integrar con clientes AI.
Uso:
  python -m bc_server.BusinessCentralMCP
"""

import os
import sys
import asyncio
import getpass
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# Cargar variables de entorno desde .env en la raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)

# Asegurar importaciones desde el paquete raíz
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp import MCPServer  # Usa el SDK oficial de MCP Python
from bc_server.config import config
from bc_server.client import bc_client


# Inicializar servidor MCP usando SDK oficial
server = MCPServer(
    name="BusinessCentral",
    protocol="mcp-streamable-1.0",
    host=os.getenv("MCP_HOST", "0.0.0.0"),
    port=int(os.getenv("MCP_PORT", 8000))
)

# Handler para tools/list (descubrimiento automático de herramientas)
@server.method("tools/list")
async def list_tools():
    """
    Devuelve la lista de herramientas MCP disponibles para discovery automático.
    Incluye inputSchema para compatibilidad con Copilot Studio.
    """
    return {
        "tools": [
            {
                "name": "get_customers", 
                "description": "Lista clientes de Business Central",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Número máximo de clientes a retornar",
                            "default": 10
                        }
                    }
                }
            },
            {
                "name": "get_customer_details", 
                "description": "Muestra detalles de un cliente por ID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "ID único del cliente en Business Central"
                        }
                    },
                    "required": ["customer_id"]
                }
            },
            {
                "name": "get_items", 
                "description": "Lista artículos de Business Central",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Número máximo de artículos a retornar",
                            "default": 10
                        }
                    }
                }
            },
            {
                "name": "get_sales_orders", 
                "description": "Lista órdenes de venta de Business Central",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Número máximo de órdenes a retornar",
                            "default": 5
                        }
                    }
                }
            },
            {
                "name": "create_customer", 
                "description": "Crea un nuevo cliente en Business Central",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "displayName": {
                            "type": "string",
                            "description": "Nombre del cliente"
                        },
                        "type": {
                            "type": "string",
                            "description": "Tipo de cliente",
                            "default": "Company"
                        },
                        "addressLine1": {
                            "type": "string",
                            "description": "Dirección principal"
                        },
                        "city": {
                            "type": "string",
                            "description": "Ciudad"
                        },
                        "email": {
                            "type": "string",
                            "description": "Correo electrónico"
                        },
                        "phoneNumber": {
                            "type": "string",
                            "description": "Número de teléfono"
                        }
                    },
                    "required": ["displayName"]
                }
            }
        ]
    }

@server.tool()
async def get_customers(limit: int = 10):
    """Lista clientes de Business Central."""
    if not config.validate():
        return {"error": "configuración inválida"}
    return await bc_client.get_customers(top=limit)

@server.tool()
async def get_customer_details(customer_id: str):
    """Muestra detalles de un cliente por ID."""
    if not config.validate():
        return {"error": "configuración inválida"}
    result = await bc_client.get_customer(customer_id)
    return result or {"error": "cliente no encontrado"}

@server.tool()
async def get_items(limit: int = 10):
    """Lista artículos de Business Central."""
    if not config.validate():
        return {"error": "configuración inválida"}
    return await bc_client.get_items(top=limit)

@server.tool()
async def get_sales_orders(limit: int = 5):
    """Lista órdenes de venta de Business Central."""
    if not config.validate():
        return {"error": "configuración inválida"}
    return await bc_client.get_orders(top=limit)

@server.tool(name="create_customer")
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
    Todos los parámetros corresponden a los campos de la entidad Customer.
    """
    # Validación de campos obligatorios
    if not displayName or not email:
        return {"error": "Los campos 'displayName' y 'email' son obligatorios"}
    # Recomendación de incluir taxRegistrationNumber
    if not taxRegistrationNumber:
        # se puede optar por un warning o log, aquí devolvemos advertencia
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

def main():
    # Despliega el servidor MCP
    server.run()

if __name__ == "__main__":
    main()