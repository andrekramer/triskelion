import sys
import asyncio
import aiohttp
import time
import json

from config import schedule
from config import models, comparison_models, configure
import support
from comparison import make_comparison

debug = False

def display(buffer, text):
  print(text)
  buffer.append(text)

async def multi_way_query(prompt, max_models = 10):
  """Query the configured models in parallel and gather the responses. """
  promises = []
  async with aiohttp.ClientSession() as session:

    i = 0
    for model in models:
      if schedule[model.name]:
        promise = model.ask(session, model.make_query(prompt))
        promises.append(promise)
        i += 1
        if i == max_models:
          break

    responses = await asyncio.gather(*promises)
  
  return responses

def clean(str):
  str1 = str.replace("\n", "\\n")
  str2 = str1.replace('"', '\\"')
  return str2

def parse_responses(responses, buffer, verbose=False):
  """Parsing out the model specific text field. Display responses if display flag is True"""
  response_texts = []
  i = 0
  for model in models:
    if not schedule[model.name]:
      if verbose: display(buffer, "skiped " + model.name)
      continue
    if verbose: display(buffer, "model " + model.name)
    json_data = json.loads(responses[i])
    json_formatted_str = json.dumps(json_data, indent=2)
    if debug: print(json_formatted_str)
    text = support.search_json(json_data, model.text_field)
    if text != None and text.strip() != "":
      if verbose: display(buffer, text)
      response_texts.append(text)
    else:
      if verbose: display(buffer, "No response text found!")
      response_texts.append("")
    i += 1
    if i == len(responses):
      break
  return response_texts


async def compare(session, model, comparison, buffer, verbose = False):
  query = model.make_query(clean(comparison))
  if debug: print(query)
  response = await model.ask(session, query)
  json_data = json.loads(response)
  if verbose:
    json_formatted_str = json.dumps(json_data, indent=2)
    if debug: print(json_formatted_str)
  text = support.search_json(json_data, model.text_field)
  if text is None:
    if verbose: display(buffer, "comparison failed")
    return False
  if verbose: display(buffer, "comparison result:\n" + text)

  if text.find("YES") != -1 and not text.find("NO") != -1:
    return True
  else:
    return False

async def compare_one_way(prompt, response_texts, buffer, verbose = False):
  """Compare the first two non blank result texts. Return None if no matches"""
  texts = [item for item in response_texts if item.strip() != ""]
  if len(texts) < 2:
    display(buffer, "Not enough responses to compare")
    return None
  
  alice = texts[0]
  bob = texts[1]

  comparison = make_comparison(prompt, "Alice", alice, "Bob", bob)
  if verbose: display(buffer, comparison)

  async with aiohttp.ClientSession() as session:
    model = comparison_models[0]

    if await compare(session, model, comparison, verbose):
        return alice
    else:
        return None
    

async def compare_two_or_three_way(prompt, response_texts, two_way_only, buffer, verbose = False):
  """Compare the first 3 non blank result texts 2 or 3 way. Return None if no matches"""
  texts = [item for item in response_texts if item.strip() != ""]
  if len(texts) < 3:
    display(buffer, "Not enough responses to compare")
    return None
  
  # 3 way comparison is possible
  alice = texts[0]
  bob = texts[1]
  eve = texts[2]

  comparison1 =  make_comparison(prompt, "Alice", alice, "Bob", bob)
  if verbose: display(buffer, comparison1)

  async with aiohttp.ClientSession() as session:
    model = comparison_models[0]

    if await compare(session, model, comparison1, verbose):
        return alice
    else:
        comparison2 =  make_comparison(prompt, "Alice", alice, "Eve", eve)
        if verbose: display(buffer, comparison2)

        model = comparison_models[1]

        if await compare(session, model, comparison2, verbose):
          return alice
        else:
           if two_way_only:
             return None
           
           comparison3 =  make_comparison(prompt, "Bob", bob, "Eve", eve)
           if verbose: display(buffer, comparison3)

           model = comparison_models[2]

           if await compare(session, model, comparison3, verbose):
              return bob
          
    return None

async def compare_all_three(prompt, response_texts, buffer, verbose=False):
  """Compare the first 3 non blank result texts in parallel"""
  texts = [item for item in response_texts if item.strip() != ""]
  if len(texts) < 3:
    display(buffer, "Not enough responses to compare")
    return None
 
  alice = texts[0]
  bob = texts[1]
  eve = texts[2]

  comparison1 = make_comparison(prompt, "Alice", alice, "Bob", bob)
  if verbose: display(buffer, comparison1)

  comparison2 = make_comparison(prompt, "Alice", alice, "Eve", eve)
  if verbose: display(buffer, comparison2)
  
  comparison3 = make_comparison(prompt, "Bob", bob, "Eve", eve)
  if verbose: display(buffer, comparison3)
 
  async with aiohttp.ClientSession() as session:
    promises = []
    model = comparison_models[0]
    promise = compare(session, model, comparison1, verbose)
    promises.append(promise)

    model = comparison_models[1]
    promise = compare(session, model, comparison2, verbose)
    promises.append(promise)

    model = comparison_models[2]
    promise = compare(session, model, comparison3, verbose)
    promises.append(promise)

    responses = await asyncio.gather(*promises)

  if verbose:
    display(buffer, "Alice and Bob " +  ("agree" if responses[0] else "disagree"))
    display(buffer, "Alice and Eve " +  ("agree" if responses[1] else "disagree"))
    display(buffer, "Bob and Eve " +  ("agree" if responses[2] else "disagree"))

  if all(responses):
    display(buffer, "**concensus**")

  if responses[0]:
    return alice
  if responses[1]:
    return alice
  if responses[2]:
    return bob
  
  return None

def n_ways(buffer, verbose=False):
  m = []
  pairs = []
  for model in models:
    if schedule[model.name]:
      m.append(model)
  for i in range(len(m) - 1):
    for j in range(i + 1, len(m)):
      if verbose: display(buffer, m[i].name + " <-> " + m[j].name)
      pairs.append((m[i], m[j], False))
  return pairs

async def compare_n_way(prompt, response_texts, buffer, verbose=False):
  run_models = []
  response_map = {}
  r = 0
  for model in models:
    if schedule[model.name]:
      if debug:
        print("response from " + model.name)
        print(response_texts[r])
      run_models.append(model)
      response_map[model.name] = response_texts[r]
      r += 1
  
  quorums = {}
  promises = []
  comparison_pairs = n_ways(buffer, True)
  
  async with aiohttp.ClientSession() as session:

    for comparison_pair in comparison_pairs:
      comparison = make_comparison(prompt, 
                                   "John (using " + comparison_pair[0].name + ")",
                                   response_map[comparison_pair[0].name],
                                   "Jane (using " + comparison_pair[1].name + ")",
                                   response_map[comparison_pair[1].name])
      if verbose: display(buffer, comparison)
 
      comparison_model = None
      for cm in comparison_models:
        if cm.name != comparison_pair[0].name and cm.name != comparison_pair[1].name:
          comparison_model = cm
          break
      if comparison_model is None:
        raise "Couldn't find a comparison model to use for n-way comparison"
      else:
        if verbose: display(buffer, "comparison model to use: " + comparison_model.name)

      promise = compare(session, comparison_model, comparison, verbose)
      promises.append(promise)

    responses = await asyncio.gather(*promises)

  r = 0
  # go over the comparison results
  for comparison in comparison_pairs:
    model1, model2, compare_result = comparison
    compare_result = responses[r] # record the updated boolean response
    if verbose: display(buffer, "quorum " + model1.name + " <--> " + model2.name + " result " + str(compare_result))
    r += 1
    if compare_result:
      quorum = quorums.get(model1.name)
      if quorum is None:
        quorums[model1.name] = quorum = []
      quorum.append(model2.name)
      quorum = quorums.get(model2.name)
      if quorum is None:
        quorums[model2.name] = quorum = []
      quorum.append(model1.name)
  
  # display the largest quorum (first if more than one with same size)
  quorum = None
  quorum_size = 0
  model_count = 0
  for model in run_models:
    model_count += 1
    q = quorums.get(model.name)
    if q is not None and len(q) > quorum_size:
      quorum = model.name
      quorum_size = len(q) + 1

  if quorum is None:
    if verbose: display(buffer, "No quorum found. All disagree.")
  else:
    if verbose: display(buffer, "quorum " + quorum + " of " + str(quorum_size))
    q = quorums[quorum]
    if verbose: display(buffer, quorum)
    for model_name in q:
      if verbose: display(buffer, model_name)
    if quorum_size == model_count:
      if verbose: display(buffer, "**concensus**")
      return response_map[quorum]
    elif quorum_size > model_count / 2:
      if verbose: display(buffer, "**quorum majority achieved**")
      return response_map[quorum]
    elif quorum_size == 2:
       if verbose: display(buffer, "Two agree")

  return None


async def run_comparison(prompt, action):
  buffer = []

  if action == "1-way":
    max_models = 2
  elif action in ["2-way", "3-way", "3-all"]:
    max_models = 3
  else:
    max_models = 10

  responses = await multi_way_query(prompt, max_models)

  texts = parse_responses(responses, buffer, True)

  compared_text = None

  if action == "1-way":
    compared_text = await compare_one_way(prompt, texts, buffer, True)
  elif action == "2-way":
    compared_text = await compare_two_or_three_way(prompt, texts, True, buffer, True)
  elif action == "3-way":
    compared_text = await compare_two_or_three_way(prompt, texts, False, buffer, True)
  elif action == "3-all":
    compared_text = await compare_all_three(prompt, texts, buffer, True)
  elif action == "n-way":
    compared_text = await compare_n_way(prompt, texts, buffer, True)
  elif action == "none":
    return buffer
  else:
    display(buffer, "unknown compare action " + action)
    return buffer

  if compared_text is not None:
    display(buffer, "compared response")
    display(buffer, compared_text)
  else:
    display(buffer, "comparison FAIL")

  return buffer

async def timed_comparison(prompt, action):
  start_time = time.time()

  await run_comparison(prompt, action)

  end_time = time.time()
  print(f"Time taken: {end_time - start_time:.2f} seconds")

async def main():

  if len(sys.argv) > 2:
    action = sys.argv[1]
    prompt = clean(sys.argv[2])
  else:
    print(
"""Usage: python3 multillm.py 3-way|2-way|1-way|none|3-all|n-way query
          -- use query as a prompt for multiple models and perform a comparison.
             1-way compare two responses
             2-way compare first response with second and third response
             3-way compare three responses to see if any two agree
             3-all compare three responses all ways
             n-way compare all the responses each way
             none can be used to just query and not do a comparison

          python3 multillm.py xyz input
          -- read input until EOF (Ctrl-D) and use the read input as the prompt with xyz comparison action

          python3 multillm.py xyz interactive
          --- start an interactive loop to read prompts. You can end this using Crtl-C or by typing "bye"
          """)
    exit()

  configure()

  if prompt == "interactive": 
    while True:
      prompt = input("prompt>")
      p = prompt.strip()
      if p == "":
        continue
      if p == "bye":
        break
      
      await timed_comparison(prompt, action)
    return
  
  if prompt == "input":
    prompt = sys.stdin.read()
  
  await timed_comparison(prompt, action)

if __name__ == "__main__":
  asyncio.run(main())
