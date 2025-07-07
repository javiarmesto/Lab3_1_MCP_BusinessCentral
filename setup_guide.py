"""
setup_guide.py

Script formativo para validar y configurar el entorno del MCP Server de Business Central:
  - Carga variables de entorno desde `.env` en distintas ubicaciones.
  - Verifica credenciales de Azure AD mediante Client Credentials.
  - Prueba llamadas a la API de Business Central (CompanyInformation, lista de compañías).
  - Imprime resultados y errores para guiar al usuario sobre la configuración necesaria.

Uso:
  python setup_guide.py
"""

import os
import asyncio
import httpx
import logging
from dotenv import load_dotenv

# Intentar cargar .env en la raíz y luego en este directorio
load_dotenv()  # carga .env en workspace root, si existe
local_env = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(local_env)
# También intentar cargar el .env original si existe en la raíz
bc_env = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(bc_env)

# Configuración global de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("setup_guide")
logger.debug(f"Cargando .env local desde: {local_env}")
logger.debug(f"Cargando .env raíz desde: {bc_env}")

async def test_azure_connection():
    logger.info("🔹 Probando conexión con Azure AD...")
    logger.debug(f"AZURE_TENANT_ID = {os.getenv('AZURE_TENANT_ID')}")
    logger.debug(f"AZURE_CLIENT_ID = {os.getenv('AZURE_CLIENT_ID')}")
    logger.debug(f"AZURE_CLIENT_SECRET = {os.getenv('AZURE_CLIENT_SECRET')}")
    tid = os.getenv("AZURE_TENANT_ID")
    cid = os.getenv("AZURE_CLIENT_ID")
    sec = os.getenv("AZURE_CLIENT_SECRET")
    if not all([tid, cid, sec]):
        logger.error("❌ Azure AD vars missing")
        return False
    url = f"https://login.microsoftonline.com/{tid}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": sec,
        "scope": "https://api.businesscentral.dynamics.com/.default"
    }
    async with httpx.AsyncClient() as cli:
        r = await cli.post(url, data=data, timeout=30)
    if r.status_code == 200:
        logger.info("✅ Azure OK")
    else:
        logger.error(f"❌ Azure error {r.status_code}")
    return r.status_code == 200

async def test_bc():
    logger.info("🔹 Probando llamada a Business Central...")
    tid = os.getenv("AZURE_TENANT_ID")
    cid = os.getenv("AZURE_CLIENT_ID")
    sec = os.getenv("AZURE_CLIENT_SECRET")
    comp = os.getenv("BC_COMPANY_ID")
    env = os.getenv("BC_ENVIRONMENT", "production")
    token_url = f"https://login.microsoftonline.com/{tid}/oauth2/v2.0/token"
    form = {
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": sec,
        "scope": "https://api.businesscentral.dynamics.com/.default"
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(token_url, data=form, headers=headers)
        logger.debug(f"TOKEN status: {resp.status_code}")
        if resp.status_code != 200:
            logger.error(f"❌ BC token error: {resp.status_code}")
            return False
        token = resp.json().get("access_token")
        if not token:
            logger.error("❌ No access_token in response")
            return False
        # Construir URL de BC sin tenant_id en path, usando environment
        url = (
            f"https://api.businesscentral.dynamics.com/v2.0/{env}/api/v2.0/"
            f"companies({comp})/CompanyInformation"
        )
        logger.debug(f"BC GET URL: {url}")
        r = await client.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=30)
        logger.debug(f"BC GET status: {r.status_code}")
        if r.status_code == 200:
            logger.info("✅ BC OK")
        else:
            logger.error(f"❌ BC error {r.status_code}")
        return r.status_code == 200

async def main():
    logger.info("Iniciando pruebas de setup para BC MCP Server...")
    if not await test_azure_connection(): return
    if not await test_bc(): return
    logger.info("\n✅ Setup completado. Ahora ejecuta: python -m BusinessCentralMCP")

if __name__ == "__main__":
    asyncio.run(main())
