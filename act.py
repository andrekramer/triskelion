"""Example of how to use run_agent """
import asyncio
from config import Config
import support
import agent
from multillm import multillm_agent

MAX_STEPS = 10

async def main():
    """Agent Plan, Test, Act loop - world and goal are read from files"""

    Config.set_trail_only(False)

    world = support.read_file_as_string("world.txt")
    if world is None:
        print("Error reading world.txt")
        return
    goal = support.read_file_as_string("goal.txt")
    if goal is None:
        print("Error reading goal.txt")
        return

    world = agent.observe(f"<world>{world}</world>")
    print("-" * 80)
    print(world)
    print("-" * 80)
    for i in range(MAX_STEPS):
        try:
            response_lines, plan, world, done = await agent.run_agent(multillm_agent, goal, world)
            if done:
                break
            print(i)
            print("-" * 80)
            print(world)
            print("-" * 80)
        except ValueError as err:
            print(str(err))

if __name__ == "__main__":
    asyncio.run(main())
