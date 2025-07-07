"""
azure_auth.py

Objetivo:
---------
Gestionar la autenticación OAuth2 con Azure AD (Entra ID) usando el flujo Client Credentials,
incluyendo cache de tokens y helpers asíncronos para obtener y renovar el token de acceso.

Este módulo centraliza la obtención de tokens para acceder a la API de Business Central desde Python,
siguiendo las mejores prácticas de seguridad y eficiencia.

Referencias:
- https://learn.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow
- https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/administration/azure-active-directory
"""

# =============================
# IMPORTS Y DEPENDENCIAS
# =============================
import asyncio
import httpx
from datetime import datetime, timedelta
from typing import Optional
from config import config


# =============================
# CLASE PRINCIPAL DE GESTIÓN DE TOKENS
# =============================
class AzureTokenManager:
    def __init__(self):
        # Token actual y expiración
        self._token: Optional[str] = None
        self._expires: Optional[datetime] = None
        # Scope de acceso para Business Central
        self._scope = "https://api.businesscentral.dynamics.com/.default"


    # =============================
    # MÉTODO PRIVADO: ¿Token válido?
    # =============================
    def _valid(self) -> bool:
        return self._token and self._expires and datetime.utcnow() < self._expires


    # =============================
    # OBTENER TOKEN (público, preferido)
    # =============================
    async def get_token(self) -> Optional[str]:
        """
        Devuelve un token válido, renovando si es necesario.
        """
        if self._valid():
            return self._token
        return await self._fetch()


    # =============================
    # MÉTODO PRIVADO: Solicitar nuevo token a Azure AD
    # =============================
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


    # =============================
    # MÉTODO ALTERNATIVO: Solicitar token (simula Postman)
    # =============================
    async def _acquire_new_token(self) -> Optional[str]:
        """
        Adquiere un nuevo token de Azure AD usando un body URL-encoded (útil para debugging avanzado).
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


# =============================
# SINGLETON GLOBAL PARA USO EN TODO EL PROYECTO
# =============================
token_manager = AzureTokenManager()