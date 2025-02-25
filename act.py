"""Example of how to use run_agent """
import asyncio

import agent
from multillm import multillm_agent

STEPS = 3

async def main():
    """Example main function"""

    world = "x = 1" + \
        "\ny = 1"
    goal = "x incremented by one"

    world = agent.observe(f"<world>{world}</world>")
    print("-" * 80)
    print(world)
    print("-" * 80)
    for i in range(STEPS):
        try:
            response_lines, plan, world = await agent.run_agent(multillm_agent, goal, world)
            print("-" * 80)
            print(world)
            print("-" * 80)
        except ValueError as err:
            print(str(err))

if __name__ == "__main__":
    asyncio.run(main())
