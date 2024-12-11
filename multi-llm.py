import sys
import asyncio
import aiohttp
import time

import gemini
import claud
import openai
import grok
import llama

async def main():
  if len(sys.argv) > 1:
    prompt = sys.argv[1]
  else:
    print("No command-line arguments provided.")
    exit()

  start_time = time.time()

  promises = []
  async with aiohttp.ClientSession() as session:
    if False:
      gemini_promise = gemini.ask(session, gemini.make_query(prompt))
      promises.append(gemini_promise)
    
    if False:
      claud_promise = claud.ask(session, claud.make_query(prompt))
      promises.append(claud_promise)

    if False:
      openai_promise = openai.ask(session, openai.make_query(prompt))
      promises.append(openai_promise)

    if False:
      grok_promise = grok.ask(session, grok.make_query(prompt))
      promises.append(grok_promise)

    if True:
      llama_promise = llama.ask(session, llama.make_query(prompt))
      promises.append(llama_promise)

    results = await asyncio.gather(*promises)

    for result in results:
      print(result)

  end_time = time.time()
  print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
  asyncio.run(main())
