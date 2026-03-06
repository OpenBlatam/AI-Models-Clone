# OpenClaw Agents SDK

El SDK de Agentes de OpenClaw proporciona una interfaz de alto nivel (fácil de usar) para crear, gestionar e invocar agentes autónomos capaces de razonar y usar herramientas en su entorno (ReAct, Embodied RL).

## Inicialización Básica

Para instanciar un agente, puedes usar la clase principal `AgentClient`. 

```python
import asyncio
from optimization_core.agents import AgentClient

async def main():
    # Inicializa el cliente
    client = AgentClient(use_swarm=False)
    
    # Habilitar herramientas
    client.add_tool("web_search")
    client.add_tool("python_execute")
    client.add_tool("file_read")
    client.add_tool("file_write")
    
    # Ejecutar una instrucción en el agente
    response = await client.run(user_id="demo_user", prompt="Busca qué es OpenClaw y guárdalo en openclaw.txt")
    print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

## Modo Swarm (Enjambre Multi-Agente)

El SDK cuenta con un Orquestador Swarm que redirige automáticamente las consultas al agente experto correcto.

```python
async def swarm_demo():
    client = AgentClient(use_swarm=True)
    
    # El swarm enviará automáticamente esto al MarketingAgent
    res1 = await client.run("user_1", "Necesito una estrategia de contenido SEO para mi SaaS.")
    
    # El swarm enviará automáticamente esto al RLAgent
    res2 = await client.run("user_1", "Optimiza este embudo publicitario.")
```

## Memoria

Cada `AgentClient` mantiene una base de datos SQLite para las interacciones. Los agentes recuerdan el contexto basado en el `user_id`. Para limpiar la memoria:

```python
await client.clear_memory("user_1")
```

## Arquitectura Interna

Los agentes están construidos bajo las siguientes carpetas en `optimization_core/agents`:
- `razonamiento_planificacion/`: Contiene el orquestador ReAct y las Tools.
- `marketing_intelligence/`: Agentes con prompts base enfocados en Marketing.
- `embodied_rl/`: Agentes que interactúan como políticas de RL en simulaciones.
- `multi_agentes/`: Orquestadores de jerarquía y routing.
