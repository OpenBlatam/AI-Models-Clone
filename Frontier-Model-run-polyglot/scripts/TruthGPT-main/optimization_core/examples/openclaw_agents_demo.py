"""
Demo de OpenClaw Agents SDK
Este script demuestra cómo usar el AgentClient interactuando con herramientas.
"""

import asyncio
import os
import sys

# Ajustar el path para permitir imports directos si se ejecuta desde examples/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents import AgentClient

async def run_single_agent():
    print("=" * 50)
    print("Iniciando Demo de Agente Único (OpenClaw Base)")
    print("=" * 50)
    
    client = AgentClient(use_swarm=False)
    
    # Agregando capacidades al agente
    client.add_tool("web_search")
    client.add_tool("python_execute")
    
    user = "demo_developer"
    
    prompt_1 = "Busca información sobre el precio de Bitcoin hoy."
    print(f"\n[Usuario]: {prompt_1}")
    response = await client.run(user_id=user, prompt=prompt_1)
    print(f"\n[Agente]: {response}")

    prompt_2 = "Escribe un script en python que calcule 5 años de interés compuesto al 10% anual para 1000 dólares."
    print(f"\n[Usuario]: {prompt_2}")
    response = await client.run(user_id=user, prompt=prompt_2)
    print(f"\n[Agente]: {response}")

async def run_swarm():
    print("\n" + "=" * 50)
    print("Iniciando Demo de Swarm (Multi-Agentes)")
    print("=" * 50)
    
    # El modo swarm carga RLAgent, MarketingAgent, etc.
    client = AgentClient(use_swarm=True)
    user = "demo_manager"
    
    prompt_1 = "Quiero una estrategia SEO y de marketing de contenidos para vender software."
    print(f"\n[Usuario]: {prompt_1}")
    response = await client.run(user_id=user, prompt=prompt_1)
    print(f"\n[Swarm -> MarketingAgent]: {response}")

    prompt_2 = "Optimiza la conversión interactuando con mi entorno."
    print(f"\n[Usuario]: {prompt_2}")
    response = await client.run(user_id=user, prompt=prompt_2)
    print(f"\n[Swarm -> RLAgent]: {response}")

if __name__ == "__main__":
    asyncio.run(run_single_agent())
    asyncio.run(run_swarm())
