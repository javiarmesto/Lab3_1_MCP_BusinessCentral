"""
client.py

Este módulo define BusinessCentralClient, un cliente HTTP asíncrono y resiliente para
la API de Business Central:
  - Obtiene y refresca tokens Azure AD automáticamente.
  - Implementa lógica de reintentos y manejo de errores HTTP.
  - Expone métodos asíncronos:
      * get_customers(top)
      * get_customer(id)
      * get_items(top)
      * get_orders(top)
"""
import asyncio
import httpx
from typing import Any, Dict, List, Optional
from bc_server.config import config
from auth.azure_auth import token_manager

class BusinessCentralClient:
    def __init__(self):
        self.base = config.bc.base_url
        self.comp = config.bc.company_id
        self._retries = 3
        self._timeout = 30

    async def _request(
        self, method: str, path: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.base}/companies({self.comp})/{path}"
        for i in range(self._retries):
            # DEBUG: mostrar intento de solicitud
            url = f"{self.base}/companies({self.comp})/{path}"
            print(f"[DEBUG] BC Request #{i+1}: {method} {url} params={params} data={data}")
            token = await token_manager.get_token()
            if not token:
                return None
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            async with httpx.AsyncClient(timeout=self._timeout) as cli:
                resp = await cli.request(method, url, headers=headers, params=params, json=data)
            # DEBUG: mostrar respuesta
            print(f"[DEBUG] BC Response {resp.status_code}: {resp.text[:200]}")
            if resp.status_code in (200, 201):
                return resp.json()
            if resp.status_code == 401:
                token_manager._token = None
                continue
            if resp.status_code >= 500:
                await asyncio.sleep(2 ** i)
                continue
            break
        print(f"[ERROR] BC API {method} {path}: {resp.status_code}")
        return None

    async def get_customers(self, top: int = 20) -> List[Dict]:
        res = await self._request("GET", f"customers", params={"$top": top})
        return res.get("value", []) if res else []

    async def get_customer(self, cid: str) -> Optional[Dict]:
        return await self._request("GET", f"customers({cid})")

    async def get_items(self, top: int = 20) -> List[Dict]:
        res = await self._request("GET", "items", params={"$top": top})
        return res.get("value", []) if res else []

    async def get_orders(self, top: int = 10) -> List[Dict]:
        res = await self._request("GET", "salesOrders", params={"$top": top})
        return res.get("value", []) if res else []

    async def create_customer(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Crea un nuevo cliente en Business Central.
        :param data: diccionario con los campos del nuevo cliente según la API de BC.
        :return: respuesta JSON del nuevo cliente o None en caso de error.
        """
        # POST a la colección 'customers'
        return await self._request("POST", "customers", data=data)

# Instancia compartida
bc_client = BusinessCentralClient()
