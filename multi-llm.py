import sys
import asyncio
import aiohttp
import time
import json

import support

import gemini
import claud
import openai
import grok
import llama

# Which models to query:
schedule = {
  "gemini": True,
  "claud": False,
  "openai": False,
  "grok": False,
  "llama": False
}

# Where in the json to find the text reply:
text_field = {
  "gemini": "text",
  "claud": "text",
  "openai": "content",
  "grok": "content",
  "llama": "content"
}

# model versions to use for queries:
models = {
  "gemini": "gemini-1.5-flash-latest",
  "claud": "claude-3-5-sonnet-20241022",
  "openai": "gpt-4o",
  "grok": "grok-beta",
  "llama":  "llama3.3-70b"
}

# The order of results (skiping any not in schedule)
order = ["gemini", "claud", "openai", "grok", "llama"]

gemini.model = models["gemini"]
claud.model = models["claud"]
openai.model = models["openai"]
grok.model = models["grok"]
llama.model = models["llama"]

async def main():
  
  if len(sys.argv) > 1:
    prompt = sys.argv[1].replace("\n", "\\n");
  else:
    print("No command-line arguments provided.")
    exit()

  start_time = time.time()

  promises = []
  async with aiohttp.ClientSession() as session:
    if schedule["gemini"]:
      gemini_promise = gemini.ask(session, gemini.make_query(prompt))
      promises.append(gemini_promise)
    
    if schedule["claud"]:
      claud_promise = claud.ask(session, claud.make_query(prompt))
      promises.append(claud_promise)

    if schedule["openai"]:
      openai_promise = openai.ask(session, openai.make_query(prompt))
      promises.append(openai_promise)

    if schedule["grok"]:
      grok_promise = grok.ask(session, grok.make_query(prompt))
      promises.append(grok_promise)

    if schedule["llama"]:
      llama_promise = llama.ask(session, llama.make_query(prompt))
      promises.append(llama_promise)

    results = await asyncio.gather(*promises)

    i = 0
    for o in order:
      if not schedule[o]:
        print("skiped " + o)
        continue
      print("model " + o)
      json_data = json.loads(results[i])
      i += 1
      json_formatted_str = json.dumps(json_data, indent=2)
      print(json_formatted_str)
      text = support.search_json(json_data, text_field[o])
      if text != None:
        print(text)
      else: 
        print("No text found")

  end_time = time.time()
  print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
  asyncio.run(main())
