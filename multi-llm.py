import sys
import asyncio
import aiohttp
import time

import gemini
import claud
import openai

async def main():
  if len(sys.argv) > 1:
    prompt = sys.argv[1]
  else:
    print("No command-line arguments provided.")
    exit()

  start_time = time.time()

  async with aiohttp.ClientSession() as session:
    if True:
      gemini_reply = await gemini.ask(session, gemini.make_query(prompt))

      print(gemini_reply)

    if True:
      claud_reply = await claud.ask(session, claud.make_query(prompt))

      print(claud_reply)

    if True:
      openai_reply = await openai.ask(session, openai.make_query(prompt))

      print(openai_reply)

  end_time = time.time()
  print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
  asyncio.run(main())
