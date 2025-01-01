# Example of how to use run_comparison from multillm

# Uncomment and use the package import as needed:
# from triskelion import multillm
# import multillm
import multillm

import asyncio

async def main():
    prompt = "roll a die"
    response = await multillm.run_comparison(prompt, "3-way")

    print(response[-2])
    print(response[-1])

if __name__ == "__main__":
  asyncio.run(main())
