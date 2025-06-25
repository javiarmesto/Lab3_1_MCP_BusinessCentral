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
from dotenv import load_dotenv
# Cargar variables de entorno
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
env_path = os.path.join(project_root, '.env')
if os.path.exists(env_path):
    load_dotenv(env_path, override=True)
else:
    raise FileNotFoundError(f".env file not found at {env_path}. Please ensure the file is correctly placed.")
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from bc_server.config import config
from bc_server.client import bc_client

app = FastAPI(
    title="Business Central MCP API",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs"
)

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
async def http_get_customers(limit: int = Query(10, ge=1, le=100)):
    """
    Lista clientes de Business Central.
    - limit: máximo número de registros a devolver
    """
    if not config.validate():
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        data = await bc_client.get_customers(top=limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/customers", response_model=Customer, status_code=201)
async def http_create_customer(customer_data: CustomerCreate):
    """
    Crea un nuevo cliente en Business Central.
    Utiliza el modelo CustomerCreate para validar los datos de entrada.
    """
    if not config.validate():
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        # Mapear CustomerCreate a el dict que espera bc_client.create_customer
        # El cliente espera campos como 'displayName', 'email', 'phoneNumber', etc.
        # y los campos de dirección anidados bajo 'address'.
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
        # Filtrar valores None del payload para no enviarlos
        customer_payload = {k: v for k, v in customer_payload.items() if v is not None}
        if customer_payload.get("address"):
            customer_payload["address"] = {k: v for k, v in customer_payload["address"].items() if v is not None}
            if not customer_payload["address"]:
                del customer_payload["address"] # Eliminar clave 'address' si está vacía

        created_customer = await bc_client.create_customer(customer_payload)
        # Asumiendo que create_customer devuelve un dict que se puede mapear a Customer
        # Es posible que necesites ajustar este mapeo según la respuesta real de bc_client.create_customer
        return Customer(
            number=created_customer.get("number", "N/A"), # BC usualmente genera el 'number'
            displayName=created_customer.get("displayName"),
            email=created_customer.get("email"),
            phoneNumber=created_customer.get("phoneNumber"),
            # Mapear la dirección de la respuesta si está presente
            address=f'{created_customer.get("address", {}).get("street", "")}, {created_customer.get("address", {}).get("city", "")}'.strip(', '),
            city=created_customer.get("address", {}).get("city"),
            country=created_customer.get("address", {}).get("countryLetterCode")
        )
    except HTTPException as e:
        # Re-lanzar HTTPExceptions para que FastAPI las maneje
        raise e
    except Exception as e:
        # Capturar otras excepciones y devolver un error 500 genérico
        # Considera loggear el error 'e' para depuración
        raise HTTPException(status_code=500, detail=f"Error al crear el cliente: {str(e)}")

@app.get("/customers/{customer_id}", response_model=Customer)
async def http_get_customer(customer_id: str):
    """
    Detalle de un cliente por ID.
    """
    if not config.validate():
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        result = await bc_client.get_customer(customer_id)
        if not result:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/items", response_model=List[Item])
async def http_get_items(limit: int = Query(10, ge=1, le=100)):
    """
    Lista de artículos de Business Central.
    """
    if not config.validate():
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        data = await bc_client.get_items(top=limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders", response_model=List[Order])
async def http_get_orders(limit: int = Query(5, ge=1, le=100)):
    """
    Lista de órdenes de venta de Business Central.
    """
    if not config.validate():
        raise HTTPException(status_code=400, detail="Configuración inválida")
    try:
        data = await bc_client.get_orders(top=limit)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    """Chequeo de salud del servicio."""
    return {"status": "ok"}
