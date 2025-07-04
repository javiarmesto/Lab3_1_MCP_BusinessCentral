"""
http_server.py

Este módulo crea un servicio HTTP REST con FastAPI para exponer las herramientas MCP de Business Central:
  - GET /customers?limit={limit}: devuelve una lista de clientes.
  - GET /customers/{customer_id}: muestra los detalles de un cliente.
  - GET /items?limit={limit}: devuelve la lista de artículos.
  - GET /orders?limit={limit}: devuelve la lista de órdenes de venta.
  - GET /health: endpoint de verificación de salud.

Al arrancar con Uvicorn, genera automáticamente la documentación Swagger en /docs
y el descriptor OpenAPI en /openapi.json, listo para consumir desde Power Platform o cualquier cliente HTTP.
"""
from typing import List, Optional
import os
import logging
from dotenv import load_dotenv
# Cargar variables de entorno solo si existe .env (local). En Azure, las variables ya están en el entorno.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    # En Azure, las variables ya están en el entorno, no es necesario .env
    pass
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query, Request
from pydantic import BaseModel
from bc_server.config import config
from bc_server.client import bc_client

# Configuración global de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("http_server")

app = FastAPI(
    title="Business Central MCP API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs"
)
logger.info("FastAPI Business Central MCP API inicializado.")

class Customer(BaseModel):
    # Campos de entidad Cliente en Business Central
    number: str
    displayName: str
    email: Optional[str] = None
    phoneNumber: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None

class Item(BaseModel):
    # Campos de entidad Artículo en Business Central
    id: str
    displayName: str
    description: Optional[str] = None
    unitPrice: Optional[float] = None
    inventory: Optional[int] = None
    unitOfMeasure: Optional[str] = None

class Order(BaseModel):
    # Campos de entidad Orden de venta en Business Central
    id: str
    orderNumber: str
    totalAmount: Optional[float] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    orderDate: Optional[datetime] = None

class CustomerCreate(BaseModel):
    """
    Modelo Pydantic para la creación de clientes.
    Define los campos requeridos y opcionales para crear un nuevo cliente.
    """
    displayName: str
    email: str
    phoneNumber: Optional[str] = None
    addressLine1: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    taxRegistrationNumber: Optional[str] = None

@app.get("/customers", response_model=List[Customer])
async def http_get_customers(limit: int = Query(10, ge=1, le=100), request: Request = None):
    """
    Lista clientes de Business Central.
    - limit: máximo número de registros a devolver
    """
    logger.info(f"GET /customers?limit={limit} desde {request.client.host if request else 'N/A'}")
    if not config.validate():
        logger.error("Configuración inválida al acceder a /customers")
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        data = await bc_client.get_customers(top=limit)
        logger.info(f"Clientes devueltos: {len(data)}")
        return data
    except Exception as e:
        logger.exception("Error en GET /customers")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/customers", response_model=Customer, status_code=201)
async def http_create_customer(customer_data: CustomerCreate, request: Request = None):
    """
    Crea un nuevo cliente en Business Central.
    Utiliza el modelo CustomerCreate para validar los datos de entrada.
    """
    logger.info(f"POST /customers desde {request.client.host if request else 'N/A'}: {customer_data.displayName}")
    if not config.validate():
        logger.error("Configuración inválida al crear cliente")
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        customer_payload = {
            "displayName": customer_data.displayName,
            "email": customer_data.email,
            "phoneNumber": customer_data.phoneNumber,
            "address": {
                "street": customer_data.addressLine1,
                "city": customer_data.city,
                "countryLetterCode": customer_data.country
            },
            "taxRegistrationNumber": customer_data.taxRegistrationNumber
        }
        customer_payload = {k: v for k, v in customer_payload.items() if v is not None}
        if customer_payload.get("address"):
            customer_payload["address"] = {k: v for k, v in customer_payload["address"].items() if v is not None}
            if not customer_payload["address"]:
                del customer_payload["address"]

        created_customer = await bc_client.create_customer(customer_payload)
        logger.info(f"Cliente creado: {created_customer.get('number', 'N/A')}")
        return Customer(
            number=created_customer.get("number", "N/A"),
            displayName=created_customer.get("displayName"),
            email=created_customer.get("email"),
            phoneNumber=created_customer.get("phoneNumber"),
            address=f'{created_customer.get("address", {}).get("street", "")}, {created_customer.get("address", {}).get("city", "")}'.strip(', '),
            city=created_customer.get("address", {}).get("city"),
            country=created_customer.get("address", {}).get("countryLetterCode")
        )
    except HTTPException as e:
        logger.warning(f"HTTPException en POST /customers: {e.detail}")
        raise e
    except Exception as e:
        logger.exception("Error al crear el cliente")
        raise HTTPException(status_code=500, detail=f"Error al crear el cliente: {str(e)}")

@app.get("/customers/{customer_id}", response_model=Customer)
async def http_get_customer(customer_id: str, request: Request = None):
    """
    Detalle de un cliente por ID.
    """
    logger.info(f"GET /customers/{customer_id} desde {request.client.host if request else 'N/A'}")
    if not config.validate():
        logger.error("Configuración inválida al consultar cliente")
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        result = await bc_client.get_customer(customer_id)
        if not result:
            logger.warning(f"Cliente {customer_id} no encontrado")
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error en GET /customers/{customer_id}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items", response_model=List[Item])
async def http_get_items(limit: int = Query(10, ge=1, le=100), request: Request = None):
    """
    Lista de artículos de Business Central.
    """
    logger.info(f"GET /items?limit={limit} desde {request.client.host if request else 'N/A'}")
    if not config.validate():
        logger.error("Configuración inválida al acceder a /items")
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        data = await bc_client.get_items(top=limit)
        logger.info(f"Artículos devueltos: {len(data)}")
        return data
    except Exception as e:
        logger.exception("Error en GET /items")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders", response_model=List[Order])
async def http_get_orders(limit: int = Query(5, ge=1, le=100), request: Request = None):
    """
    Lista de órdenes de venta de Business Central.
    """
    logger.info(f"GET /orders?limit={limit} desde {request.client.host if request else 'N/A'}")
    if not config.validate():
        logger.error("Configuración inválida al acceder a /orders")
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        data = await bc_client.get_orders(top=limit)
        logger.info(f"Órdenes devueltas: {len(data)}")
        return data
    except Exception as e:
        logger.exception("Error en GET /orders")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mcp")
async def mcp_proxy(request: Request):
    """
    Endpoint MCP avanzado: maneja solicitudes JSON-RPC para tools/list y tools/call.
    Compatible con Copilot Studio y clientes MCP.
    """
    try:
        body = await request.json()
        method = body.get("method")
        logger.info(f"POST /mcp método: {method} desde {request.client.host if request else 'N/A'}")
        
        # Manejar tools/list
        if method == "tools/list":
            return {
                "jsonrpc": "2.0",
                "result": {
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
                },
                "id": body.get("id")
            }
        
        # Manejar tools/call
        elif method == "tools/call":
            params = body.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            # Ejecutar la herramienta correspondiente
            if tool_name == "get_customers":
                limit = arguments.get("limit", 10)
                data = await bc_client.get_customers(top=limit)
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": str(data)}]},
                    "id": body.get("id")
                }
            elif tool_name == "get_items":
                limit = arguments.get("limit", 10)
                data = await bc_client.get_items(top=limit)
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": str(data)}]},
                    "id": body.get("id")
                }
            elif tool_name == "get_sales_orders":
                limit = arguments.get("limit", 5)
                data = await bc_client.get_orders(top=limit)
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": str(data)}]},
                    "id": body.get("id")
                }
            elif tool_name == "get_customer_details":
                customer_id = arguments.get("customer_id")
                if not customer_id:
                    raise HTTPException(status_code=400, detail="customer_id requerido")
                data = await bc_client.get_customer(customer_id)
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": str(data)}]},
                    "id": body.get("id")
                }
            elif tool_name == "create_customer":
                data = await bc_client.create_customer(arguments)
                return {
                    "jsonrpc": "2.0",
                    "result": {"content": [{"type": "text", "text": str(data)}]},
                    "id": body.get("id")
                }
            else:
                return {
                    "jsonrpc": "2.0",
                    "error": {"code": -32601, "message": f"Herramienta no encontrada: {tool_name}"},
                    "id": body.get("id")
                }
        
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": f"Método no soportado: {method}"},
                "id": body.get("id")
            }
            
    except Exception as e:
        logger.exception("Error en endpoint MCP")
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": f"Error interno: {str(e)}"},
            "id": body.get("id") if hasattr(body, 'get') else "unknown"
        }

@app.get("/health")
def health_check(request: Request = None):
    """Chequeo de salud del servicio."""
    logger.info(f"GET /health desde {request.client.host if request else 'N/A'}")
    return {"status": "ok"}

@app.get("/sse", tags=["Agentic", "McpSse"])
async def mcp_sse_endpoint(sessionId: Optional[str] = Query(None), request: Request = None):
    """
    Endpoint MCP SSE para Copilot Studio.
    Compatible con el protocolo Server-Sent Events para agentes.
    """
    logger.info(f"GET /sse desde {request.client.host if request else 'N/A'} - sessionId: {sessionId}")
    
    # Respuesta de herramientas disponibles en formato MCP SSE
    return {
        "jsonrpc": "2.0",
        "id": sessionId or "auto-generated",
        "method": "tools/list",
        "result": {
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
    }
