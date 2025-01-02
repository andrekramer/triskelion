import sys
import asyncio
import aiohttp
import time
import json

# Add current directory to import path when using this file as a module. Say with "from <some-dir> import multillm".
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from config import models, schedule, comparison_models, comparison_schedule, configure
from config import get_diff_comparator, max_no_models, set_trail_only, display, debug, client_timeout_seconds
import support
from comparison import make_comparison

timeout = aiohttp.ClientTimeout(total=client_timeout_seconds)

def getSession():
   return aiohttp.ClientSession(timeout=timeout) 

def get_model(i):
  for model in models:
     if not schedule[model.name]:
       continue
     if i == 0:
       return model
     else:
        i -= 1

def get_comparison_model(i):
  for cm in comparison_models:
    if not comparison_schedule[cm.name]:
      continue
    if i == 0:
      return cm
    else:
      i -= 1
  return get_comparison_model(i)

def get_diff_comparison_model(model1, model2):
  comparison_model = None
  for cm in comparison_models:
    if not comparison_schedule[cm.name]:
      continue
    if cm.name != model1.name and cm.name != model2.name:
      comparison_model = cm
      break
  if comparison_model is None:
    raise RuntimeError("Couldn't find a different comparison model to use for comparison")
  else:
    return comparison_model

async def multi_way_query(prompt, max_models = max_no_models):
  """Query the configured models in parallel and gather the responses. """
  promises = []
  async with getSession() as session:

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

def parse_responses(responses, trail, verbose=False):
  """Parsing out the model specific text field. Display responses if display flag is True"""
  response_texts = []
  i = 0
  for model in models:
    if not schedule[model.name]:
      if debug: display(trail, "skiped " + model.name)
      continue
    if verbose: display(trail, "model " + model.name)
    response = responses[i]
    if response is None or response == "":
      response = "{}"
    
    json_data = json.loads(response)
    json_formatted_str = json.dumps(json_data, indent=2)
    if debug: print(json_formatted_str)
    text = support.search_json(json_data, model.text_field)
    if text != None and text.strip() != "":
      if verbose: display(trail, text)
      response_texts.append(text)
    else:
      if verbose: display(trail, "No response text found!")
      response_texts.append("")
    i += 1
    if i == len(responses):
      break
  return response_texts

async def compare(session, model, comparison, trail, verbose = False):
  if comparison is None or comparison == "":
    return False
  
  query = model.make_query(clean(comparison))
  if debug: print(query)
  response = await model.ask(session, query)
  if response is None or response.strip() == "":
    response = "{}"
  json_data = json.loads(response)
  if verbose:
    json_formatted_str = json.dumps(json_data, indent=2)
    if debug: print(json_formatted_str)
  text = support.search_json(json_data, model.text_field)
  if text is None:
    if verbose: display(trail, f"comparison using {model.name} failed!")
    return False
  if verbose: display(trail, f"comparison using {model.name} result:\n" + text)

  if text.find("YES") != -1 and text.find("NO") == -1:
    return True
  else:
    return False


async def compare_one_way(prompt, texts, trail, verbose = False):
  """Compare the first two result texts. Return None if no matches"""
  if len(texts) < 2:
    display(trail, "Not enough responses to compare")
    return None
  
  alice = texts[0]
  bob = texts[1]

  comparison = make_comparison(prompt, "Alice", alice, "Bob", bob)
  if debug: display(trail, comparison)

  async with getSession() as session:
    if get_diff_comparator():
      model = get_diff_comparison_model(get_model(0), get_model(1))
    else:
      model = get_comparison_model(0)
    if verbose: display(trail, f"using model {model.name} for comparison")
    if await compare(session, model, comparison, verbose):
      if verbose: display(trail, f"comparison {model.name} succeeds, can use {get_model(0).name}")
      return alice
    else:
      return None
    

async def compare_two_or_three_way(prompt, texts, two_way_only, trail, verbose = False):
  """Compare the first 3 result texts 2 or 3 way. Return None if no matches"""
  if len(texts) < 3:
    display(trail, "Not enough responses to compare!")
    return None
  
  # 3 way comparison is possible
  alice = texts[0]
  bob = texts[1]
  eve = texts[2]

  comparison1 =  make_comparison(prompt, "Alice", alice, "Bob", bob)
  if debug: display(trail, comparison1)

  async with getSession() as session:
    
    if get_diff_comparator():
      model = get_diff_comparison_model(get_model(0), get_model(1))
    else:
      model = get_comparison_model(0)
    if verbose: display(trail, f"using model {model.name} for comparison")

    if await compare(session, model, comparison1, verbose):
        if verbose: display(trail, f"comparison {model.name} succeeds, can use {get_model(0).name}")
        return alice
    else:
        comparison2 =  make_comparison(prompt, "Alice", alice, "Eve", eve)
        if debug: display(trail, comparison2)

        if get_diff_comparator():
          model = get_diff_comparison_model(get_model(0), get_model(2))
        else:
          model = get_comparison_model(1)
        if verbose: display(trail, f"using model {model.name} for comparison")

        if await compare(session, model, comparison2, verbose):
          if verbose: display(trail, f"comparison {model.name} succeeds, can use {get_model(0).name}")
          return alice
        else:
          if two_way_only:
            return None
           
          comparison3 =  make_comparison(prompt, "Bob", bob, "Eve", eve)
          if debug: display(trail, comparison3)

          if get_diff_comparator():
            model = get_diff_comparison_model(get_model(1), get_model(2))
          else:
            model = get_comparison_model(2)
          if verbose: display(trail, f"using model {model.name} for comparison")

          if await compare(session, model, comparison3, verbose):
            if verbose: display(trail, f"comparison {model.name} succeeds, can use {get_model(1).name}")
            return bob

    return None

async def compare_all_three(prompt, texts, trail, verbose=False):
  """Compare the first 3 result texts in parallel"""
  if len(texts) < 3:
    display(trail, "Not enough responses to compare!")
    return None
 
  alice = texts[0]
  bob = texts[1]
  eve = texts[2]

  comparison1 = make_comparison(prompt, "Alice", alice, "Bob", bob)
  if debug:
    display(trail, "Alice and Bob")
    display(trail, comparison1)

  comparison2 = make_comparison(prompt, "Alice", alice, "Eve", eve)
  if debug:
    display(trail, "Alice and Eve")
    display(trail, comparison2)
  
  comparison3 = make_comparison(prompt, "Bob", bob, "Eve", eve)
  if debug:
    display(trail, "Bob and Eve")
    display(trail, comparison3)
 
  async with getSession() as session:
    promises = []
   
    if get_diff_comparator():
      model = get_diff_comparison_model(get_model(0), get_model(1))
    else:
      model = get_comparison_model(0)
    if verbose: display(trail, f"using model {model.name} for comparison 0")

    promise = compare(session, model, comparison1, verbose)
    promises.append(promise)

    if get_diff_comparator():
      model = get_diff_comparison_model(get_model(0), get_model(2))
    else:
      model = get_comparison_model(1)
    if verbose: display(trail, f"using model {model.name} for comparison 1")

    promise = compare(session, model, comparison2, verbose)
    promises.append(promise)

    if get_diff_comparator():
      model = get_diff_comparison_model(get_model(1), get_model(2))
    else:
      model = get_comparison_model(2)
    if verbose: display(trail, f"using model {model.name} for comparison 2")

    promise = compare(session, model, comparison3, verbose)
    promises.append(promise)

    responses = await asyncio.gather(*promises)

  if verbose:
    display(trail, "Alice and Bob " +  ("agree" if responses[0] else "fail to agree"))
    display(trail, "Alice and Eve " +  ("agree" if responses[1] else "fail to agree"))
    display(trail, "Bob and Eve " +  ("agree" if responses[2] else "fail to agree"))

  if all(responses):
    display(trail, "**concensus**")

  if responses[0]:
    return alice
  if responses[1]:
    return alice
  if responses[2]:
    return bob
  
  return None

async def compare_two_first(prompt, texts, trail, verbose=False):
  """Compare 2 result texts first and only use a third if first 3 disagree """
  if len(texts) < 2:
    display(trail, "Not enough responses to compare!")
    return None
 
  alice = texts[0]
  bob = texts[1]

  comparison1 = make_comparison(prompt, "Alice", alice, "Bob", bob)
  if debug: display(trail, comparison1)

  async with getSession() as session:
    if get_diff_comparator():
      model = get_diff_comparison_model(get_model(0), get_model(1))
    else:
      model = get_comparison_model(0)
    if verbose: display(trail, "Compare first two responses using " + model.name)
    response = await compare(session, model, comparison1, verbose)
    if response:
      display(trail, f"first two models agree, can use {get_model(0).name}")
      return alice
    
    # Get 3rd model text
    i = 0
    text3 = ""
    
    for model in models:
      if schedule[model.name]:
        if i == 2:
          display(trail, "Query next model " + model.name)
          model3 = model
          response = await model.ask(session, model.make_query(prompt))
          if response is not None and response.strip() != "":
            json_data = json.loads(response)
            text3 = support.search_json(json_data, model.text_field)
          else:
            text3 = ""
          break
        else:
          i += 1

    if text3 == "":
      display(trail, "3rd model failed to answer!")
      return None
    else:
      display(trail, "model " + model3.name)
      display(trail, text3)
      
    eve = text3
    comparison2 = make_comparison(prompt, "Alice", alice, "Eve", eve)
    if debug: display(trail, comparison2)
  
    if get_diff_comparator():
      model = get_diff_comparison_model(get_model(1), get_model(2))
    else:
      model = get_comparison_model(1)
    if verbose: display(trail, "Compare first and third using " + model.name)
    response = await compare(session, model, comparison2, verbose)
    if response:
      display(trail, f"first and third agree, can use {get_model(0).name}")
      return alice
  
    comparison3 = make_comparison(prompt, "Bob", bob, "Eve", eve)
    if debug: display(trail, comparison3)

    if get_diff_comparator():
      model = get_diff_comparison_model(get_model(1), get_model(2))
    else:
      model = get_comparison_model(2)
    if verbose: display(trail, "Compare second and third using " + model.name)
    response = await compare(session, model, comparison3, verbose)
    if response:
     display(trail, f"second and third agree, can use {get_model(1).name}")
    return bob
  
  display(trail, "none agree")
  return None
   

def n_ways(trail, verbose=False):
  m = []
  pairs = []
  max = max_no_models
  for model in models:
    if max == 0:
      break
    if schedule[model.name]:
      m.append(model)
      max -= 1
  for i in range(len(m) - 1):
    for j in range(i + 1, len(m)):
      if verbose: display(trail, m[i].name + " <-> " + m[j].name)
      pairs.append((m[i], m[j], False))
  return pairs


async def compare_n_way(prompt, response_texts, trail, verbose=False):
  run_models = []
  comp_models = []
  response_map = {}
  r = 0
  for model in models:
    if r == max_no_models:
      break
    if schedule[model.name]:
      if debug:
        print("response from " + model.name)
        print(response_texts[r])
      run_models.append(model)
      response_map[model.name] = response_texts[r]
      r += 1
  
  quorums = {}
  promises = []
  comparison_pairs = n_ways(trail, True)
  
  async with getSession() as session:

    for comparison_pair in comparison_pairs:
      comparison = make_comparison(prompt, 
                                   "John (using " + comparison_pair[0].name + ")",
                                   response_map[comparison_pair[0].name],
                                   "Jane (using " + comparison_pair[1].name + ")",
                                   response_map[comparison_pair[1].name])
      if debug: display(trail, comparison)
 
      comparison_model = get_diff_comparison_model(comparison_pair[0], comparison_pair[1])
      if debug: display(trail, "comparison model selected: " + comparison_model.name)
      comp_models.append(comparison_model)

      promise = compare(session, comparison_model, comparison, verbose)
      promises.append(promise)

    responses = await asyncio.gather(*promises)

  r = 0
  # go over the comparison results
  for comparison in comparison_pairs:
    model1, model2, compare_result = comparison
    if debug: display(trail, "Comparison response " + str(responses[r]))
    compare_result = responses[r] # record the updated boolean response
    if verbose: display(trail, "comparison " + model1.name + " <--> " + model2.name + " (using " + comp_models[r].name + ") " + ("agree" if compare_result else "fail to agree"))
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
    if verbose: display(trail, "No quorum found.")
  else:
    if verbose: display(trail, "quorum " + quorum + " of " + str(quorum_size))
    q = quorums[quorum]
    if verbose: display(trail, quorum)
    for model_name in q:
      if verbose: display(trail, model_name)
    if quorum_size == model_count:
      if verbose: display(trail, "**concensus**")
      return response_map[quorum]
    elif quorum_size > model_count / 2:
      if verbose: display(trail, "**quorum majority achieved**")
      return response_map[quorum]
    elif quorum_size == 2:
       if verbose: display(trail, "two agree")

  return None


async def run_comparison(prompt, action):
  trail = []

  if action == "1-way" or action == "2-1":
    max_models = 2
  elif action in ["2-way", "3-way", "3-all"]:
    max_models = 3
  else:
    max_models = max_no_models

  responses = await multi_way_query(prompt, max_models)

  texts = parse_responses(responses, trail, True)

  compared_text = None

  if action == "1-way":
    compared_text = await compare_one_way(prompt, texts, trail, True)
  elif action == "2-way":
    compared_text = await compare_two_or_three_way(prompt, texts, True, trail, True)
  elif action == "3-way":
    compared_text = await compare_two_or_three_way(prompt, texts, False, trail, True)
  elif action == "2-1":
    compared_text = await compare_two_first(prompt, texts, trail, True)
  elif action == "3-all":
    compared_text = await compare_all_three(prompt, texts, trail, True)
  elif action == "n-way":
    compared_text = await compare_n_way(prompt, texts, trail, True)
  elif action == "none":
    display(trail, "first response:")
    display(trail, texts[0])
    return trail
  else:
    display(trail, "unknown compare action " + action)
    return trail

  if compared_text is not None:
    display(trail, "PASS compared response")
    display(trail, compared_text)
  else:
    display(trail, "FAIL comparison")
    display(trail, "")

  return trail

async def timed_comparison(prompt, action):
  start_time = time.time()

  await run_comparison(prompt, action)

  end_time = time.time()
  print(f"Time taken: {end_time - start_time:.2f} seconds")

async def main():
  set_trail_only(False)

  if len(sys.argv) > 2:
    action = sys.argv[1]
    prompt = clean(sys.argv[2])
  else:
    print(
"""Usage: python3 multillm.py 3-way|2-way|1-way|none|2-1|3-all|n-way prompt
          -- use given text as a prompt for multiple models and perform a comparison.
             1-way compare two responses
             2-way compare first response with second and third response
             3-way compare three responses to see if any two agree
             2-1 compare 2 responses and go on to a third only if first two fail to agree
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
