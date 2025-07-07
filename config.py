"""
config.py

Módulo centralizado de configuración para la aplicación MCP de Microsoft Dynamics 365 Business Central.

Características principales:
  - Carga automática de variables de entorno desde `.env` (seguridad y portabilidad).
  - Valida la presencia de credenciales de Azure AD (tenant_id, client_id, client_secret).
  - Obtiene y valida parámetros de Business Central (environment, company_id, tenant_id).
  - Expone modelos Pydantic para tipado y validación:
      * AzureADConfig: configuración de autenticación Azure AD.
      * BusinessCentralConfig: configuración de la API de BC.
  - Crea una instancia global `config` con los valores validados y accesibles en toda la app.

Onboarding rápido:
  1. Configura el archivo `.env` con las variables requeridas (ver README).
  2. Usa `config.azure_ad` y `config.bc` para acceder a la configuración en cualquier módulo.
  3. Llama a `config.validate()` para comprobar la validez antes de lanzar operaciones críticas.

Referencias útiles:
  - Configuración de autenticación: https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-add-app-roles-in-azure-ad-apps
  - APIs REST de Business Central: https://learn.microsoft.com/en-us/dynamics365/business-central/dev-itpro/webservices/api-overview
  - Blog TechSphereDynamics: https://techspheredynamics.com
"""
import os
import logging
from dotenv import load_dotenv, find_dotenv
from typing import Optional
from pydantic import BaseModel, Field, model_validator
import sys

# Cargar .env automáticamente si existe, incluso en procesos de recarga de Uvicorn
env_path = find_dotenv()
if env_path:
    load_dotenv(env_path, override=True)

# Configuración global de logging (si no está ya configurado)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("config")


class AzureADConfig(BaseModel):
    """
    Modelo de configuración para autenticación Azure AD.
    Incluye tenant_id, client_id, client_secret y authority (calculado si no se provee).
    """
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
    """
    Modelo de configuración para la API de Business Central.
    Incluye environment, company_id, tenant_id y base_url (calculada si no se provee).
    """
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
    """
    Clase principal de configuración de la app MCP.
    Expone las secciones azure_ad y bc, y métodos de validación.
    """
    def __init__(self):
        self.azure_ad = self._load_azure()
        self.bc = self._load_bc()

    def _load_azure(self) -> AzureADConfig:
        """
        Carga y valida la configuración de Azure AD desde variables de entorno.
        Lanza ValueError si falta alguna variable crítica.
        """
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
        """
        Carga y valida la configuración de Business Central desde variables de entorno.
        Lanza ValueError si falta BC_COMPANY_ID.
        """
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
        """
        Valida que la configuración cargada sea consistente y completa.
        Retorna True si es válida, False si falta algún campo crítico.
        """
        try:
            assert self.azure_ad.tenant_id
            assert self.azure_ad.client_id
            assert self.azure_ad.client_secret
            assert self.bc.company_id
            return True
        except AssertionError as e:
            logger.error(f"Configuración inválida: {e}")
            return False


# Instancia compartida para uso global
config = AppConfig()
