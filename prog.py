"""Example of how to use run_comparison from multillm"""
import asyncio

# Uncomment and use the package import as needed:
# from triskelion import multillm
# import multillm
import multillm

async def main():
    """Example main function"""
    prompt = "roll a die"
    response = await multillm.run_comparison(prompt, "3-way")

    print(response[-2]) # PASS or FAIL?
    print(response[-1]) # the response if a PASS

if __name__ == "__main__":
    asyncio.run(main())
