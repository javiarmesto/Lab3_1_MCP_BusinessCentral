"""
test_mcp_client.py

Cliente MCP simple para probar los endpoints del servidor MCP Business Central.
Este script permite invocar las herramientas MCP de Business Central desplegadas
en Azure App Service o en local.

Uso:
    python test_mcp_client.py

Ejemplo:
    # Listar 5 clientes
    python test_mcp_client.py get_customers 5
    
    # Detalles de un cliente específico
    python test_mcp_client.py get_customer_details "CLIENTE01"
    
    # Listar 10 artículos
    python test_mcp_client.py get_items 10
    
    # Listar 3 órdenes de venta
    python test_mcp_client.py get_sales_orders 3
    
    # Crear un nuevo cliente
    python test_mcp_client.py create_customer "Empresa Nueva" "contacto@empresa.com" "912345678" "Calle Principal 123" "Madrid" "ES" "B12345678"
"""
import sys
import json
import asyncio
import argparse
from typing import Any, Dict, List, Optional, Union
import httpx

# URL del servidor MCP (cambia a la URL de Azure o local según necesites)
# Para servidor local:
# MCP_SERVER_URL = "http://localhost:8000/mcp"
# Para Azure App Service:
MCP_SERVER_URL = "https://mcp-bc-javi-chb7bue4evbkeyb0.westeurope-01.azurewebsites.net/mcp"

async def invoke_mcp_tool(tool_name: str, params: Dict[str, Any] = None) -> Any:
    """
    Invoca una herramienta MCP en el servidor Business Central.
    
    Args:
        tool_name: Nombre de la herramienta a invocar
        params: Parámetros para la herramienta (opcional)
    
    Returns:
        Respuesta de la herramienta MCP
    """
    if params is None:
        params = {}
    
    # Crear la solicitud MCP según el protocolo
    mcp_request = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "runTool",
        "params": {
            "name": tool_name,
            "parameters": params
        }
    }
    
    # Hacer la solicitud HTTP POST al servidor MCP
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                MCP_SERVER_URL,
                json=mcp_request,
                headers={"Content-Type": "application/json"}
            )
            
            # Comprobar si la solicitud fue exitosa
            response.raise_for_status()
            
            # Analizar la respuesta JSON
            result = response.json()
            
            # Comprobar si hay un error en la respuesta MCP
            if "error" in result:
                print(f"Error MCP: {result['error']['message']}")
                if "data" in result["error"]:
                    print(f"Detalles: {result['error']['data']}")
                return None
            
            # Devolver el resultado
            return result.get("result", {})
            
        except httpx.HTTPStatusError as e:
            print(f"Error HTTP: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            print(f"Error de conexión: {e}")
        except Exception as e:
            print(f"Error inesperado: {e}")
        
        return None

async def main():
    parser = argparse.ArgumentParser(description="Cliente MCP para Business Central")
    parser.add_argument("tool", help="Nombre de la herramienta MCP a invocar")
    parser.add_argument("args", nargs="*", help="Argumentos para la herramienta")
    
    args = parser.parse_args()
    tool_name = args.tool
    tool_args = args.args
    
    # Configurar parámetros según la herramienta
    params = {}
    
    if tool_name == "get_customers":
        if tool_args:
            params["limit"] = int(tool_args[0])
    
    elif tool_name == "get_customer_details":
        if not tool_args:
            print("Error: Se requiere el ID del cliente")
            return
        params["customer_id"] = tool_args[0]
    
    elif tool_name == "get_items":
        if tool_args:
            params["limit"] = int(tool_args[0])
    
    elif tool_name == "get_sales_orders":
        if tool_args:
            params["limit"] = int(tool_args[0])
    
    elif tool_name == "create_customer":
        if len(tool_args) < 2:
            print("Error: Se requieren al menos nombre y email")
            return
        
        params["displayName"] = tool_args[0]
        params["email"] = tool_args[1]
        
        if len(tool_args) > 2:
            params["phoneNumber"] = tool_args[2]
        if len(tool_args) > 3:
            params["addressLine1"] = tool_args[3]
        if len(tool_args) > 4:
            params["city"] = tool_args[4]
        if len(tool_args) > 5:
            params["country"] = tool_args[5]
        if len(tool_args) > 6:
            params["taxRegistrationNumber"] = tool_args[6]
    
    else:
        print(f"Error: Herramienta '{tool_name}' no reconocida")
        return
    
    print(f"Invocando herramienta: {tool_name}")
    print(f"Parámetros: {json.dumps(params, indent=2)}")
    
    # Invocar la herramienta MCP
    result = await invoke_mcp_tool(tool_name, params)
    
    if result is not None:
        print("\nResultado:")
        print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
