"""
config.py

Este módulo centraliza la configuración de la aplicación Business Central MCP:
  - Carga variables de entorno (.env) automáticamente.
  - Valida que existan las credenciales de Azure AD (tenant_id, client_id, client_secret).
  - Obtiene parámetros de Business Central (environment, company_id).
  - Expone dos modelos Pydantic:
      * AzureADConfig: configuración de autenticación de Azure AD.
      * BusinessCentralConfig: configuración de la API de Business Central.
  - Crea una instancia global `config` con los valores validados.
"""
import os
from dotenv import load_dotenv, find_dotenv
# Cargar .env automáticamente si existe, incluso en procesos de recarga de Uvicorn
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path, override=True)
from typing import Optional
from pydantic import BaseModel, Field, model_validator
import sys

# Note: Environment variables should be loaded by the main module before importing this

class AzureADConfig(BaseModel):
    tenant_id: str = Field(..., description="Azure AD Tenant ID")
    client_id: str = Field(..., description="Azure AD Application ID")
    client_secret: str = Field(..., description="Azure AD Client Secret")
    authority: Optional[str] = None

    @model_validator(mode="after")
    def set_authority(self):
        # Establece authority si no se suministra
        if not self.authority:
            self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        return self

class BusinessCentralConfig(BaseModel):
    environment: str = Field(default="production", description="BC Environment")
    company_id: str = Field(..., description="Business Central Company ID")
    tenant_id: str = Field(..., description="Azure AD Tenant ID for BC API path")
    base_url: Optional[str] = None

    def __post_init__(self):
        if not self.base_url:
            # Construye la URL base incluyendo tenant_id y environment
            self.base_url = (
                f"https://api.businesscentral.dynamics.com/v2.0/"
                f"{self.tenant_id}/{self.environment}/api/v2.0"
            )

class AppConfig:
    def __init__(self):
        self.azure_ad = self._load_azure()
        self.bc = self._load_bc()

    def _load_azure(self) -> AzureADConfig:
        t = os.getenv("AZURE_TENANT_ID")
        c = os.getenv("AZURE_CLIENT_ID")
        s = os.getenv("AZURE_CLIENT_SECRET")

        # Raise if any required Azure AD variables are missing
        if not all([t, c, s]):
            missing = [v for v, val in (
                ("AZURE_TENANT_ID", t),
                ("AZURE_CLIENT_ID", c),
                ("AZURE_CLIENT_SECRET", s),
            ) if not val]
            raise ValueError(f"Faltan variables de Azure AD: {', '.join(missing)}")
        return AzureADConfig(tenant_id=t, client_id=c, client_secret=s)

    def _load_bc(self) -> BusinessCentralConfig:
        env = os.getenv("BC_ENVIRONMENT", "production")
        cid = os.getenv("BC_COMPANY_ID")
        if not cid:
            raise ValueError("Falta BC_COMPANY_ID")
        # Incluir tenant_id para construir correctamente la ruta de Business Central
        tenant = self.azure_ad.tenant_id
        bc = BusinessCentralConfig(environment=env, company_id=cid, tenant_id=tenant)
        # Construir base_url con el método __post_init__
        bc.__post_init__()
        return bc

    def validate(self) -> bool:
        try:
            assert self.azure_ad.tenant_id
            assert self.azure_ad.client_id
            assert self.azure_ad.client_secret
            assert self.bc.company_id
            return True
        except AssertionError as e:
            print(f"[ERROR] Configuración inválida: {e}")
            return False

# Instancia compartida
config = AppConfig()
