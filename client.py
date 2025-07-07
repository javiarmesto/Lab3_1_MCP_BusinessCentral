"""
client.py

Cliente HTTP asíncrono y resiliente para la API de Microsoft Dynamics 365 Business Central.

Características principales:
  - Obtiene y refresca tokens Azure AD automáticamente (OAuth2/Entra ID).
  - Implementa lógica de reintentos exponenciales y manejo robusto de errores HTTP (401, 5xx).
  - Expone métodos asíncronos para operaciones clave:
      * get_customers(top): Lista clientes
      * get_customer(id): Detalle de cliente
      * get_items(top): Lista artículos
      * get_orders(top): Lista órdenes de venta
      * create_customer(data): Crea un nuevo cliente

Onboarding rápido:
  1. Asegúrate de que el archivo `.env` esté correctamente configurado (ver README).
  2. Usa los métodos del cliente para interactuar con la API de BC desde herramientas MCP.
  3. Consulta los docstrings de cada método para ejemplos y detalles de uso.

Referencias útiles:
  - APIs REST de Business Central: https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/api-overview
  - Seguridad y autenticación: https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/enable-apis-using-azure-active-directory
  - Blog TechSphereDynamics: https://techspheredynamics.com
"""
import asyncio
import httpx
import logging
import os
from typing import Any, Dict, List, Optional
from config import config
from azure_auth import token_manager

# Configuración global de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("bc_client")


class BusinessCentralClient:
    """
    Cliente asíncrono para la API de Business Central.
    Gestiona autenticación, reintentos y expone métodos de negocio clave.
    """
    def __init__(self):
        self.base = config.bc.base_url
        self.comp = config.bc.company_id
        self._retries = 3  # Número de reintentos ante errores transitorios
        self._timeout = 30  # Timeout global para peticiones HTTP (segundos)

    async def _request(
        self, method: str, path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Realiza una petición HTTP autenticada a la API de Business Central.
        Maneja reintentos automáticos ante errores 401/5xx y refresca el token si es necesario.
        Parámetros:
            method (str): Método HTTP ('GET', 'POST', etc.)
            path (str): Ruta relativa dentro de la compañía BC
            params (dict): Parámetros de query opcionales
            data (dict): Payload JSON para POST/PUT
        Retorna:
            Diccionario con la respuesta JSON o None si falla.
        """
        url = f"{self.base}/companies({self.comp})/{path}"
        for i in range(self._retries):
            # DEBUG: mostrar intento de solicitud
            url = f"{self.base}/companies({self.comp})/{path}"
            logger.debug(f"BC Request #{i+1}: {method} {url} params={params} data={data}")
            token = await token_manager.get_token()
            if not token:
                logger.error("No se pudo obtener el token de autenticación.")
                return None
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            async with httpx.AsyncClient(timeout=self._timeout) as cli:
                resp = await cli.request(method, url, headers=headers, params=params, json=data)
            # DEBUG: mostrar respuesta
            logger.debug(f"BC Response {resp.status_code}: {resp.text[:200]}")
            if resp.status_code in (200, 201):
                return resp.json()
            if resp.status_code == 401:
                token_manager._token = None
                logger.warning("Token expirado o inválido. Reintentando...")
                continue
            if resp.status_code >= 500:
                logger.warning(f"Error {resp.status_code} en Business Central. Reintentando...")
                await asyncio.sleep(2 ** i)
                continue
            break
        logger.error(f"BC API {method} {path}: {resp.status_code}")
        return None


    async def get_customers(self, top: int = 20) -> List[Dict]:
        """
        Obtiene una lista de clientes de Business Central.
        Parámetros:
            top (int): Número máximo de clientes a retornar (default 20).
        Retorna:
            Lista de diccionarios con clientes.
        """
        res = await self._request("GET", f"customers", params={"$top": top})
        if res:
            logger.info(f"Clientes recuperados: {len(res.get('value', []))}")
        else:
            logger.error("No se pudo recuperar la lista de clientes.")
        return res.get("value", []) if res else []


    async def get_customer(self, cid: str) -> Optional[Dict]:
        """
        Obtiene el detalle de un cliente por su ID.
        Parámetros:
            cid (str): ID único del cliente en BC.
        Retorna:
            Diccionario con los datos del cliente o None si no existe.
        """
        return await self._request("GET", f"customers({cid})")


    async def get_items(self, top: int = 20) -> List[Dict]:
        """
        Lista artículos de Business Central.
        Parámetros:
            top (int): Número máximo de artículos a retornar (default 20).
        Retorna:
            Lista de diccionarios con artículos.
        """
        res = await self._request("GET", "items", params={"$top": top})
        return res.get("value", []) if res else []


    async def get_orders(self, top: int = 10) -> List[Dict]:
        """
        Lista órdenes de venta de Business Central.
        Parámetros:
            top (int): Número máximo de órdenes a retornar (default 10).
        Retorna:
            Lista de diccionarios con órdenes de venta.
        """
        res = await self._request("GET", "salesOrders", params={"$top": top})
        return res.get("value", []) if res else []


    async def create_customer(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo cliente en Business Central.
        Parámetros:
            data (dict): Diccionario con los campos del nuevo cliente según la API de BC.
        Retorna:
            Respuesta JSON del nuevo cliente o None en caso de error.
        Notas:
            - Consulta la documentación oficial para el esquema de datos requerido.
        """
        # POST a la colección 'customers'
        return await self._request("POST", "customers", data=data)


# Instancia compartida para uso global
bc_client = BusinessCentralClient()
