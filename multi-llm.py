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

# model versions to use for queries
model_versions = {
  "gemini": "gemini-1.5-flash-latest",
  "claud": "claude-3-5-sonnet-20241022",
  "openai": "gpt-4o",
  "grok": "grok-beta",
  "llama":  "llama3.3-70b"
}

# The models and order of responses (skiping any not in schedule)
models = [gemini.Gemini, claud.Claud, openai.Openai, grok.Grok, llama.Llama]

# Push down the model configuration to imported models
gemini.Gemini.model = model_versions["gemini"]
claud.Claud.model = model_versions["claud"]
openai.Openai.model = model_versions["openai"]
grok.Grok.model = model_versions["grok"]
llama.Llama.model = model_versions["llama"]

async def multi_way_query(prompt):
  """Query the configured models in parallel and gather the responses. """
  promises = []
  async with aiohttp.ClientSession() as session:

    for model in models:
      if schedule[model.name]:
        promise = model.ask(session, model.make_query(prompt))
        promises.append(promise)

    responses = await asyncio.gather(*promises)
  
  return responses

def clean(str):
  return str.replace("\n", "\\n")

def parse_responses(responses, display=False):
  """Parsing out the model specific text field. Display responses if display flag is True"""
  response_texts = []
  i = 0
  for model in models:
    if not schedule[model.name]:
      if display: print("skiped " + model.name)
      continue
    print("model " + model.name)
    json_data = json.loads(responses[i])
    i += 1
    json_formatted_str = json.dumps(json_data, indent=2)
    print(json_formatted_str)
    text = support.search_json(json_data, model.text_field)
    if text != None and text.strip() != "":
      if display: print(text)
      response_texts.append(text)
    else:
      if display: print("No text found")
      response_texts.append("")

  return response_texts

async def compare_three_way(response_texts):
  """Compare the first 3 non blank result texts. Return None if no matches"""
  texts = [item for item in response_texts if item.strip() != ""]
  if len(texts) < 3:
    print("Not enough responses to compare")
    return None
  
  # 3 way comparison is possible
  alice = clean(texts[0])
  bob = clean(texts[1])
  eve = clean(texts[2])

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

  compared_text = await compare_three_way(texts)

  if compared_text is not None:
    print("compared response")
    print(compared_text)

  end_time = time.time()
  print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
  asyncio.run(main())
