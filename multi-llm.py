import sys
import asyncio
import aiohttp
import time
import json

from config import schedule, compare_instructions
from config import models, comparison_models, configure
import support


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
  str1 = str.replace("\n", "\\n")
  str2 = str1.replace('"', '\\"')
  return str2

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
    # print(json_formatted_str)
    text = support.search_json(json_data, model.text_field)
    if text != None and text.strip() != "":
      if display: print(text)
      response_texts.append(text)
    else:
      if display: print("No response text found")
      response_texts.append("")

  return response_texts


async def compare(session, model, comparison, verbose):
  query = model.make_query(clean(comparison))
  # print(query)
  response = await model.ask(session, query)
  json_data = json.loads(response)
  if verbose:
    json_formatted_str = json.dumps(json_data, indent=2)
    print(json_formatted_str)
  text = support.search_json(json_data, model.text_field)
  if text is None:
    print("comparison failed")
    return False
  print("comparison result:\n" + text)

  if text.find("YES") != -1 and not text.find("NO") != -1:
    return True
  else:
    return False

async def compare_one_way(response_texts, verbose=False):
  """Compare the first two non blank result texts. Return None if no matches"""
  texts = [item for item in response_texts if item.strip() != ""]
  if len(texts) < 2:
    print("Not enough responses to compare")
    return None
  
  alice = texts[0]
  bob = texts[1]

  comparison = "Alice says:\n" + alice + "\n" + \
               "\nBob says:\n" + bob + "\n" + \
                compare_instructions
  if verbose: print(clean(comparison))

  async with aiohttp.ClientSession() as session:
    model = comparison_models[0]

    if await compare(session, model, comparison, verbose):
        return alice
    else:
        return None
    

async def compare_two_or_three_way(response_texts, two_way_only=False, verbose=False):
  """Compare the first 3 non blank result texts 2 or 3 way. Return None if no matches"""
  texts = [item for item in response_texts if item.strip() != ""]
  if len(texts) < 3:
    print("Not enough responses to compare")
    return None
  
  # 3 way comparison is possible
  alice = texts[0]
  bob = texts[1]
  eve = texts[2]

  comparison1 = "Alice says:\n" + alice + "\n" + \
                "\nBob says:\n" + bob + "\n" + \
                compare_instructions
  if verbose: print(clean(comparison1))

  async with aiohttp.ClientSession() as session:
    model = comparison_models[0]

    if await compare(session, model, comparison1, verbose):
        return alice
    else:
        comparison2 = "Alice says:\n" + alice + "\n" + \
                      "\nEve says:\n" + eve + "\n" + \
                      compare_instructions
        if verbose: print(clean(comparison2))

        model = comparison_models[1]

        if await compare(session, model, comparison2, verbose):
          return alice
        else:
           
           if two_way_only:
             return None
           
           comparison3 = "Bob says:\n" + bob + "\n" + \
                         "\nEve says:\n" + eve + "\n" + \
                         compare_instructions
           if verbose: print(clean(comparison3))

           model = comparison_models[2]

           if await compare(session, model, comparison3, verbose):
              return bob
          
    return None

async def compare_all_three(response_texts, verbose=False):
  """Compare the first 3 non blank result texts in parallel"""
  texts = [item for item in response_texts if item.strip() != ""]
  if len(texts) < 3:
    print("Not enough responses to compare")
    return None
 
  alice = texts[0]
  bob = texts[1]
  eve = texts[2]

  comparison1 = "Alice says:\n" + alice + "\n" + \
                "\nBob says:\n" + bob + "\n" + \
                compare_instructions
  if verbose: print(clean(comparison1))

  comparison2 = "Alice says:\n" + alice + "\n" + \
                "\nEve says:\n" + eve + "\n" + \
                compare_instructions
  if verbose: print(clean(comparison2))
  
  comparison3 = "Bob says:\n" + bob + "\n" + \
                "\nEve says:\n" + eve + "\n" + \
                compare_instructions
  if verbose: print(clean(comparison3))
 
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

  print("Alice and Bob " +  ("agree" if responses[0] else "disagree"))
  print("Alice and Eve " +  ("agree" if responses[1] else "disagree"))
  print("Bob and Eve " +  ("agree" if responses[2] else "disagree"))

  if all(responses):
    print("**concensus**")

  if responses[0]:
    return alice
  
  if responses[1]:
    return alice
  
  if responses[2]:
    return bob
  
  return None

def n_ways():
  m = []
  pairs = []
  for model in models:
    if schedule[model.name]:
      m.append(model)
  for i in range(len(m) - 1):
    for j in range(i + 1, len(m)):
      print(m[i].name + " <-> " + m[j].name)
      pairs.append((m[i], m[j], False))
  return pairs


async def compare_n_way(response_texts, verbose=False):
  run_models = []
  response_map = {}
  r = 0
  for model in models:
    if schedule[model.name]:
      if verbose:
        print("response_map " + model.name)
        print(response_texts[r])
      response_map[model.name] = response_texts[r]
      run_models.append(model)
      r += 1
  
  quorums = {}
  promises = []
  comparison_pairs = n_ways()
  
  async with aiohttp.ClientSession() as session:

    for comparison_pair in comparison_pairs:
      
      comparison = "John (using " + comparison_pair[0].name + ") says:\n" + response_map[comparison_pair[0].name] + "\n" + \
                   "\nJane (using " + comparison_pair[1].name + ") says:\n" + response_map[comparison_pair[1].name]+ "\n" + \
                   compare_instructions
      if verbose: print(clean(comparison))
 
      comparison_model = None
      for cm in comparison_models:
        if cm.name != comparison_pair[0].name and cm.name != comparison_pair[1].name:
          comparison_model = cm
          break
      if comparison_model is None:
        raise "Couldn't find a comparison model to use"
      else:
        print("comparison model to use: " + comparison_model.name)

      promise = compare(session, comparison_model, comparison, verbose)
      promises.append(promise)

    responses = await asyncio.gather(*promises)

  r = 0
  # go over the comparison results
  for comparison in comparison_pairs:
    model1, model2, compare_result = comparison
    compare_result = responses[r] # record the updated boolean response
    if verbose: print("quorum " + model1.name + " <--> " + model2.name + " result " + str(compare_result))
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
  for model in models:
    if schedule[model.name]:
      model_count += 1
      q = quorums.get(model.name)
      if q is not None and len(q) > quorum_size:
        quorum = model.name
        quorum_size = len(q) + 1

  if quorum is None:
    print("No quorum found")
  else:
    print("quorum " + quorum + " of " + str(quorum_size))
    q = quorums[quorum]
    print(quorum)
    for model_name in q:
      print(model_name)
    if quorum_size == model_count:
      print("**concensus**")
      return response_map[quorum]
    elif quorum_size > model_count / 2:
      print("**quorum majority achieved**")
      return response_map[quorum]

  return None

async def main():

  if len(sys.argv) > 2:
    action = sys.argv[1]
    prompt = clean(sys.argv[2])
  else:
    print("Usage: python3 multi-llm.py 3-way|2-way|1-way|3-all|n-way query")
    exit()

  configure()

  start_time = time.time()

  responses = await multi_way_query(prompt)

  texts = parse_responses(responses, True)

  compared_text = None

  if action == "1-way":
    compared_text = await compare_one_way(texts)
  elif action == "2-way":
    compared_text = await compare_two_or_three_way(texts, True)
  elif action == "3-way":
    compared_text = await compare_two_or_three_way(texts, False)
  elif action == "3-all":
    compared_text = await compare_all_three(texts)
  elif action == "n-way":
    compared_text = await compare_n_way(texts, True)
  else:
    print("unknown compare action " + action)

  if compared_text is not None:
    print("compared response")
    print(compared_text)
  else:
    print("comparison FAIL")

  end_time = time.time()
  print(f"Time taken: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
  asyncio.run(main())
