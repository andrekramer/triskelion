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

# Which models to query
schedule = {
  "gemini": True,
  "claud": False,
  "openai": True,
  "grok": False,
  "llama": True
}

# Where in the json to find the text reply
text_field = {
  "gemini": "text",
  "claud": "text",
  "openai": "content",
  "grok": "content",
  "llama": "content"
}

# model versions to use for queries
models = {
  "gemini": "gemini-1.5-flash-latest",
  "claud": "claude-3-5-sonnet-20241022",
  "openai": "gpt-4o",
  "grok": "grok-beta",
  "llama":  "llama3.3-70b"
}

# The order of responses (skiping any not in schedule)
order = ["gemini", "claud", "openai", "grok", "llama"]

# Push down the model configuration to imported models
gemini.model = models["gemini"]
claud.model = models["claud"]
openai.model = models["openai"]
grok.model = models["grok"]
llama.model = models["llama"]

async def multi_way_query(prompt):
  """Query the configured models in parallel and gather the responses. """
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

    responses = await asyncio.gather(*promises)
  
  return responses

def clean(str):
  return str.replace("\n", "\\n")

def parse_responses(responses, display=False):
  """Parsing out the model specific text field. Display responses if display flag is True"""
  response_texts = []
  i = 0
  for o in order:
    if not schedule[o]:
      if display: print("skiped " + o)
      continue
    print("model " + o)
    json_data = json.loads(responses[i])
    i += 1
    json_formatted_str = json.dumps(json_data, indent=2)
    print(json_formatted_str)
    text = support.search_json(json_data, text_field[o])
    if text != None:
      if display: print(text)
      response_texts.append(text)
    else:
      if display: print("No text found")

  return response_texts

async def compare_three_way(response_texts):
  """Compare the first 3 reult texts. Return None if no matches"""
  if len(response_texts) < 3:
    print("Not enough responses to compare")
    return None
  
  # 3 way comparison is possible
  alice = clean(response_texts[0])
  bob = clean(response_texts[1])
  eve = clean(response_texts[0])

  async with aiohttp.ClientSession() as session:
    pass

  return None

async def main():
  
  if len(sys.argv) > 1:
    prompt = clean(sys.argv[1]);
  else:
    print("Usage: python3 multi-llm.py query")
    exit()

  start_time = time.time()

  responses = await multi_way_query(prompt)

  texts = parse_responses(responses, True)

  compared_text = compare_three_way(texts)

  if compared_text is not None:
    print("compared response")
    print(compared_text)

  end_time = time.time()
  print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
  asyncio.run(main())
