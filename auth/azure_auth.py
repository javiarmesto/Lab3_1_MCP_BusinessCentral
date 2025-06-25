"""
Azure AD Client Credentials Flow con cache de token
"""
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Optional
from bc_server.config import config

class AzureTokenManager:
    def __init__(self):
        self._token: Optional[str] = None
        self._expires: Optional[datetime] = None
        self._scope = "https://api.businesscentral.dynamics.com/.default"

    def _valid(self) -> bool:
        return self._token and self._expires and datetime.utcnow() < self._expires

    async def get_token(self) -> Optional[str]:
        if self._valid():
            return self._token
        return await self._fetch()

    async def _fetch(self) -> Optional[str]:
        url = f"{config.azure_ad.authority}/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": config.azure_ad.client_id,
            "client_secret": config.azure_ad.client_secret,
            "scope": self._scope
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        async with httpx.AsyncClient() as cli:
            resp = await cli.post(url, data=data, headers=headers, timeout=30)
        if resp.status_code == 200:
            j = resp.json()
            self._token = j["access_token"]
            self._expires = datetime.utcnow() + timedelta(seconds=j.get("expires_in", 3600))
            return self._token
        print(f"[ERROR] Token Azure AD: {resp.status_code}")
        return None

    async def _acquire_new_token(self) -> Optional[str]:
        """
        Adquiere un nuevo token de Azure AD
        """
        token_url = f"{config.azure_ad.authority}/oauth2/v2.0/token"
        # Construimos el body como URL-encoded
        form = {
            "grant_type":    "client_credentials",
            "client_id":     config.azure_ad.client_id,
            "client_secret": config.azure_ad.client_secret,
            "scope":         self._scope
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # USAR content= y urllib.parse.urlencode para simular Postman exactamente
                import urllib.parse
                payload = urllib.parse.urlencode(form)
                response = await client.post(
                    token_url,
                    content=payload,
                    headers=headers
                )
                # DEBUG: si falla, ver body completo
                if response.status_code != 200:
                    print(f"[DEBUG] Token request failed ({response.status_code}): {response.text}")
                    return None
                data = response.json()
                access_token = data["access_token"]
                expires_in   = data.get("expires_in", 3600)
                # cache
                self._token_cache   = access_token
                self._token_expires = datetime.now() + timedelta(seconds=expires_in - 300)
                return access_token
        except Exception as e:
            print(f"[ERROR] Exception acquiring token: {e}")
            return None

token_manager = AzureTokenManager()