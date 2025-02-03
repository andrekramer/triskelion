"""Multi LLM comparisons"""
import sys
import time
import json
from pathlib import Path
import asyncio
import aiohttp

from config import models, schedule, comparison_models, comparison_schedule, configure
from config import MAX_NO_MODELS, display, DEBUG, actors, Config, TestModel
import support
from comparison import make_comparison, \
    make_critique, make_summary, make_ranking, make_combiner, make_exam, \
    add_full_stop, quote

# Add current directory to import path when using this file as a module.
# Say with "from <some-dir> import multillm".
sys.path.append(str(Path(__file__).parent))

timeout = aiohttp.ClientTimeout(total=Config.client_timeout_seconds)

def get_session():
    """get http async session with configured timeout"""
    return aiohttp.ClientSession(timeout=timeout)

def get_model(i):
    """get ith model"""
    for model in models:
        if not schedule[model.name]:
            continue
        if i == 0:
            return model
        i -= 1
    raise RuntimeError("not enough models")

def get_comparison_model(i):
    """get ith comparison model"""
    for cm in comparison_models:
        if not comparison_schedule[cm.name]:
            continue
        if i == 0:
            return cm
        i -= 1
    return get_comparison_model(i)

def get_diff_comparison_model(model1, model2, model3 = None):
    """get a different comparison model from two models passed as args"""
    comparison_model = None
    for cm in comparison_models:
        if not comparison_schedule[cm.name]:
            continue
        if cm.name not in (model1.name, model2.name, "" if model3 is None else model3.name):
            comparison_model = cm
            break

    if comparison_model is None:
        raise RuntimeError("Couldn't find a different comparison model to use for comparison")
    return comparison_model

async def multi_way_query(prompt, max_models = MAX_NO_MODELS):
    """Query the configured models in parallel and gather the responses"""
    promises = []
    async with get_session() as session:

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

def clean(s):
    """remove line breaks from string and escape \""""
    str1 = s.replace("\n", "\\n")
    str2 = str1.replace('"', '\\"')
    return str2

def parse_responses(responses, trail, verbose=False):
    """Parsing out the model specific text field. Display responses if display flag is True"""
    response_texts = []
    i = 0
    for model in models:
        if not schedule[model.name]:
            if DEBUG:
                display(trail, "skiped " + model.name)
            continue
        if verbose:
            display(trail, "model " + model.name)
        response = responses[i]
        if response is None or response == "":
            response = "{}"

        json_data = json.loads(response)
        json_formatted_str = json.dumps(json_data, indent=2)
        if DEBUG:
            print(json_formatted_str)
        text = support.search_json(json_data, model.text_field)
        if text is not None and text.strip() != "":
            if verbose:
                display(trail, text)
            response_texts.append(text)
        else:
            if verbose:
                display(trail, "No response text found!")
                print(json_formatted_str)
            response_texts.append("")
        i += 1
        if i == len(responses):
            break
    return response_texts

async def compare(session, model, comparison, trail, verbose = False):
    """compare using given model"""
    if comparison is None or comparison == "":
        return False

    query = model.make_query(clean(comparison))
    if DEBUG:
        print(query)
    response = await model.ask(session, query)
    if response is None or response.strip() == "":
        response = "{}"
    json_data = json.loads(response)
    if DEBUG:
        json_formatted_str = json.dumps(json_data, indent=2)
        print(json_formatted_str)
    text = support.search_json(json_data, model.text_field)
    if text is None:
        if verbose:
            display(trail, f"comparison using {model.name} failed!")
        return False
    if verbose:
        display(trail, f"comparison using {model.name} result:\n" + text)

    return text.find("YES") != -1 and text.find("NO") == -1

async def query_critique(session, model, critque, trail, verbose = False):
    """query for critique using given model"""

    query = model.make_query(clean(critque))
    if DEBUG:
        print(query)
    response = await model.ask(session, query)
    if response is None or response.strip() == "":
        response = "{}"
    json_data = json.loads(response)
    if DEBUG:
        json_formatted_str = json.dumps(json_data, indent=2)
        print(json_formatted_str)
    text = support.search_json(json_data, model.text_field)
    if text is None:
        if verbose:
            display(trail, f"critique using {model.name} failed!")
        return "FAIL"
    if verbose:
        display(trail, f"critique using {model.name} result:\n" + text)

    return text

def ensure_texts(texts, count, trail):
    """ensure there are enough responses to compare"""
    if len(texts) < 2:
        display(trail, "Not enough responses to compare")
        return True
    return False


async def compare_one_way(prompt, texts, trail, verbose = False):
    """Compare the first two result texts. Return None if no matches"""
    if ensure_texts(texts, 2, trail):
        return None

    alice = texts[0]
    bob = texts[1]

    comparison = make_comparison(prompt, "Alice", alice, "Bob", bob)
    if verbose:
        display(trail, comparison)

    async with get_session() as session:
        model = __get_comparator_1(trail, verbose)

        if await compare(session, model, comparison, trail, verbose):
            if verbose:
                display(trail, f"comparison {model.name} succeeds, can use {get_model(0).name}")
            return alice
        return None


async def compare_two_or_three_way(prompt, texts, two_way_only, trail, verbose = False):
    """Compare the first 3 result texts 2 or 3 way. Return None if no matches"""
    if ensure_texts(texts, 3, trail):
        return None

    # 3 way comparison is possible
    alice = texts[0]
    bob = texts[1]
    eve = texts[2]

    comparison1 =  make_comparison(prompt, "Alice", alice, "Bob", bob)
    if DEBUG:
        display(trail, comparison1)

    async with get_session() as session:

        model = __get_comparator_1(trail, verbose)

        if await compare(session, model, comparison1, trail, verbose):
            if verbose:
                display(trail, f"comparison {model.name} succeeds, can use {get_model(0).name}")
            return alice

        comparison2 =  make_comparison(prompt, "Alice", alice, "Eve", eve)
        if DEBUG:
            display(trail, comparison2)

        model = __get_comparator_2(trail, verbose)

        if await compare(session, model, comparison2, trail, verbose):
            if verbose:
                display(trail, f"comparison {model.name} succeeds, can use {get_model(0).name}")
            return alice

        if two_way_only:
            return None

        comparison3 =  make_comparison(prompt, "Bob", bob, "Eve", eve)
        if DEBUG:
            display(trail, comparison3)

        model = __get_comparator_3(trail, verbose)

        if await compare(session, model, comparison3, trail, verbose):
            if verbose:
                display(trail,
                        f"comparison {model.name} succeeds, can use {get_model(1).name}")
                return bob

        return None

def __get_comparator_3(trail, verbose):
    if Config.get_single_comparator():
        model = get_comparison_model(0)
    elif Config.get_diff_comparator():
        model = get_diff_comparison_model(get_model(1), get_model(2))
    else:
        model = get_comparison_model(2)
    if verbose:
        display(trail, f"using model {model.name} for comparison")
    return model

def __get_comparator_2(trail, verbose):
    if Config.get_single_comparator():
        model = get_comparison_model(0)
    elif Config.get_diff_comparator():
        model = get_diff_comparison_model(get_model(0), get_model(2))
    else:
        model = get_comparison_model(1)
    if verbose:
        display(trail, f"using model {model.name} for comparison")
    return model

def __get_comparator_1(trail, verbose):
    if Config.get_single_comparator():
        model = get_comparison_model(0)
    if Config.get_diff_comparator():
        model = get_diff_comparison_model(get_model(0), get_model(1))
    else:
        model = get_comparison_model(0)
    if verbose:
        display(trail, f"using model {model.name} for comparison")
    return model

def __get_second_comparator_1(model, trail, verbose):
    if Config.get_single_comparator():
        model = get_comparison_model(1)
    elif Config.get_diff_comparator():
        model = get_diff_comparison_model(get_model(0), get_model(1), model)
    else:
        model = get_comparison_model(1)
    if verbose:
        display(trail, f"using model {model.name} for second comparison")
    return model

def __get_second_comparator_2(model, trail, verbose):
    if Config.get_single_comparator():
        model = get_comparison_model(1)
    elif Config.get_diff_comparator():
        model = get_diff_comparison_model(get_model(0), get_model(2), model)
    else:
        model = get_comparison_model(2)
    if verbose:
        display(trail, f"using model {model.name} for second comparison")
    return model

def __get_second_comparator_3(model, trail, verbose):
    if Config.get_single_comparator():
        model = get_comparison_model(1)
    elif Config.get_diff_comparator():
        model = get_diff_comparison_model(get_model(1), get_model(2), model)
    else:
        model = get_comparison_model(3)
    if verbose:
        display(trail, f"using model {model.name} for third comparison")
    return model


async def compare_all_three(prompt, texts, trail, verbose=False):
    """Compare the first 3 result texts in parallel"""
    if ensure_texts(texts, 3, trail):
        return None

    alice = texts[0]
    bob = texts[1]
    eve = texts[2]

    comparison1 = make_comparison(prompt, "Alice", alice, "Bob", bob)
    if DEBUG:
        display(trail, "Alice and Bob")
        display(trail, comparison1)

    comparison2 = make_comparison(prompt, "Alice", alice, "Eve", eve)
    if DEBUG:
        display(trail, "Alice and Eve")
        display(trail, comparison2)

    comparison3 = make_comparison(prompt, "Bob", bob, "Eve", eve)
    if DEBUG:
        display(trail, "Bob and Eve")
        display(trail, comparison3)

    async with get_session() as session:
        promises = []

        model = __get_comparator_1(trail, verbose)

        promise = compare(session, model, comparison1, trail, verbose)
        promises.append(promise)

        model = __get_comparator_2(trail, verbose)

        promise = compare(session, model, comparison2, trail, verbose)
        promises.append(promise)

        model = __get_comparator_3(trail, verbose)

        promise = compare(session, model, comparison3, trail, verbose)
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
    if ensure_texts(texts, 2, trail):
        return None

    alice = texts[0]
    bob = texts[1]

    comparison1 = make_comparison(prompt, "Alice", alice, "Bob", bob)
    if DEBUG:
        display(trail, comparison1)

    async with get_session() as session:
        model = __get_comparator_1(trail, verbose)
        response = await compare(session, model, comparison1, trail, verbose)
        if response:
            display(trail, f"first two models agree, can use {get_model(0).name}")
            return alice

        # Get 3rd model text
        text3, model3 = await __ask_next_model(prompt, trail, session)

        if text3 == "":
            display(trail, "3rd model failed to answer!")
            return None

        display(trail, "model " + model3.name)
        display(trail, text3)

        eve = text3
        comparison2 = make_comparison(prompt, "Alice", alice, "Eve", eve)
        if DEBUG:
            display(trail, comparison2)

        model = __get_comparator_2(trail, verbose)
        response = await compare(session, model, comparison2, trail, verbose)
        if response:
            display(trail, f"first and third agree, can use {get_model(0).name}")
            return alice

        comparison3 = make_comparison(prompt, "Bob", bob, "Eve", eve)
        if DEBUG:
            display(trail, comparison3)

        model = __get_comparator_3(trail, verbose)
        response = await compare(session, model, comparison3, trail, verbose)
        if response:
            display(trail, f"second and third agree, can use {get_model(1).name}")
        return bob

    display(trail, "none agree")
    return None


async def compare_twice_three_way(prompt, texts, trail, verbose = False):
    """Compare the first 3 result twice. Return None if no matches"""
    if ensure_texts(texts, 3, trail):
        return None

    alice = texts[0]
    bob = texts[1]
    eve = texts[2]

    comparison1 =  make_comparison(prompt, "Alice", alice, "Bob", bob)
    if DEBUG:
        display(trail, comparison1)

    async with get_session() as session:

        responses = await __compare_1_twice(trail, verbose, comparison1, session)
        if all(responses):
            if verbose:
                display(trail, f"compare twice succeeds, can use {get_model(0).name}")
            return alice

        comparison2 =  make_comparison(prompt, "Alice", alice, "Eve", eve)
        if DEBUG:
            display(trail, comparison2)

        responses = await __compare_2_twice(trail, verbose, session, comparison2)
        if all(responses):
            if verbose:
                display(trail, f"second compare twice succeeds, can use {get_model(0).name}")
            return alice

        comparison3 =  make_comparison(prompt, "Bob", bob, "Eve", eve)
        if DEBUG:
            display(trail, comparison3)

        responses = await __compare_3_twice(trail, verbose, session, comparison3)
        if all(responses):
            if verbose:
                display(trail,
                        f"third compare twice succeeds, can use {get_model(1).name}")
            return bob

        return None

async def __compare_3_twice(trail, verbose, session, comparison3):
    model = __get_comparator_3(trail, verbose)
    model2 = __get_second_comparator_3(model, trail, verbose)

    return await __compare_twice(session, comparison3, (model, model2), trail, verbose)

async def __compare_2_twice(trail, verbose, session, comparison2):
    model = __get_comparator_2(trail, verbose)
    model2 = __get_second_comparator_2(model, trail, verbose)

    return await __compare_twice(session, comparison2, (model, model2), trail, verbose)

async def __compare_1_twice(trail, verbose, comparison1, session):
    model = __get_comparator_1(trail, verbose)
    model2 = __get_second_comparator_1(model, trail, verbose)

    return await __compare_twice(session, comparison1, (model, model2), trail, verbose)

async def __compare_twice(session, comparison, model_pair, trail, verbose):
    promise1 = compare(session, model_pair[0], comparison, trail, verbose)
    promise2 = compare(session, model_pair[1], comparison, trail, verbose)

    responses = await asyncio.gather(promise1, promise2)
    return responses

async def __ask_next_model(prompt, trail, session):
    i = 0
    text3 = ""
    model3 = None
    for model in models:
        if schedule[model.name]:
            if i == 2:
                if DEBUG:
                    display(trail, "query next model " + model.name)
                model3 = model
                text3 = await __ask_next(prompt, session, model)
                break
            i += 1
    return text3,model3

async def __ask_next(prompt, session, model):
    response = await model.ask(session, model.make_query(prompt))
    if response is not None and response.strip() != "":
        json_data = json.loads(response)
        return support.search_json(json_data, model.text_field)
    return ""

def n_ways(trail, verbose=False):
    """all n way combinations as pairs"""
    m = []
    pairs = []
    max_models = MAX_NO_MODELS
    for model in models:
        if max_models == 0:
            break
        if schedule[model.name]:
            m.append(model)
            max_models -= 1
    for i in range(len(m) - 1):
        for j in range(i + 1, len(m)):
            if verbose:
                display(trail, m[i].name + " <-> " + m[j].name)
            pairs.append((m[i], m[j]))
    return pairs


async def compare_n_way(prompt, response_texts, trail, verbose=False):
    """N way comparison"""
    run_models, comp_models, response_map = __get_run_models(response_texts)

    comparison_pairs, responses = await __ask_n(prompt, comp_models, response_map, trail, verbose)

    quorums = __add_into_quorums(comp_models, comparison_pairs, responses, trail, verbose)

    quorum, quorum_size, model_count = __calculate_quorum(run_models, quorums)

    # display the largest quorum (first if more than one with same size)
    if quorum is None:
        if verbose:
            display(trail, "No quorum found.")
        return None

    if verbose:
        display(trail, "quorum " + quorum + " of " + str(quorum_size))
    q = quorums[quorum]
    if verbose:
        display(trail, quorum)
    for model_name in q:
        if verbose:
            display(trail, model_name)
    if quorum_size == model_count:
        if verbose:
            display(trail, "**concensus**")
        return response_map[quorum]
    if quorum_size > model_count / 2:
        if verbose:
            display(trail, "**quorum majority achieved**")
        return response_map[quorum]
    if quorum_size == 2:
        if verbose:
            display(trail, "two agree")

    return None

def __add_into_quorums(comp_models, comparison_pairs, responses, trail, verbose):
    quorums = {}
    r = 0
    # go over the comparison results and add into quorums
    for comparison in comparison_pairs:
        model1, model2 = comparison
        if DEBUG:
            display(trail, "Comparison response " + str(responses[r]))
        compare_result = responses[r] # record the updated boolean response
        if verbose:
            display(trail, "comparison " + model1.name + \
                            " <--> " + model2.name + " (using " + \
                            comp_models[r].name + ") " + \
                            ("agree" if compare_result else "fail to agree"))
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
    return quorums

async def __ask_n(prompt, comp_models, response_map, trail, verbose):
    promises = []
    comparison_pairs = n_ways(trail, True)

    async with get_session() as session:
        for comparison_pair in comparison_pairs:
            comparison = make_comparison(prompt,
                                         "John (using " + comparison_pair[0].name + ")",
                                         response_map[comparison_pair[0].name],
                                         "Jane (using " + comparison_pair[1].name + ")",
                                         response_map[comparison_pair[1].name])
            if DEBUG:
                display(trail, comparison)

            comparison_model = get_diff_comparison_model(comparison_pair[0], comparison_pair[1])
            if DEBUG:
                display(trail, "comparison model selected: " + comparison_model.name)
            comp_models.append(comparison_model)

            promise = compare(session, comparison_model, comparison, trail, verbose)
            promises.append(promise)

        responses = await asyncio.gather(*promises)
    return comparison_pairs,responses

def __get_run_models(response_texts):
    run_models = []
    comp_models = []
    response_map = {}
    r = 0
    for model in models:
        if r == MAX_NO_MODELS:
            break
        if schedule[model.name]:
            if DEBUG:
                print("response from " + model.name)
                print(response_texts[r])
            run_models.append(model)
            response_map[model.name] = response_texts[r]
            r += 1
    return run_models,comp_models,response_map

def __calculate_quorum(run_models, quorums):
    quorum = None
    quorum_size = 0
    model_count = 0
    for model in run_models:
        model_count += 1
        q = quorums.get(model.name)
        if q is not None and len(q) + 1 > quorum_size:
            quorum = model.name
            quorum_size = len(q) + 1
    return quorum,quorum_size,model_count


# new comarison - add using following template here
async def compare_new_template(prompt, texts, trail, verbose=False):
    """ new comparison template """
    n_required = 3 # say
    if ensure_texts(texts, n_required, trail):
        return None

    async with get_session() as session:
        # promises = []
        # comparison = make_comparison(prompt, "Alice", texts[0], "Bob", texts[1])
        # promise = compare(session, comparison_model, comparison, verbose)
        # promises.append(promise)

        # responses = await asyncio.gather(*promises)
        # for i in range(len(texts)):
        #   if response[i]: return texts[i]
        pass

    # return the compared text or None
    return None

async def run_comparison(prompt, action):
    """run a comparison"""
    trail = []

    # new comparison - constrain the fan out here
    if action in ('1-way', '2-1'):
        max_models = 2
    elif action in ["2-way", "3-way", "3-all"]:
        max_models = 3
    else:
        max_models = MAX_NO_MODELS

    responses = await multi_way_query(prompt, max_models)

    texts = parse_responses(responses, trail, True)

    return await __run_compare_action(action, prompt, texts, trail)

async def __run_compare_action(action, prompt, texts, trail):
    # new comarison - add here
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
    elif action == "3-twice":
        compared_text = await compare_twice_three_way(prompt, texts, trail, True)
    elif action == "n-way":
        compared_text = await compare_n_way(prompt, texts, trail, True)
    elif action == "none":
        display(trail, "first response:")
        display(trail, texts[0])
        return trail
    else:
        display(trail, "FAIL")
        display(trail, "unknown compare action " + action)
        return trail

    if compared_text is not None:
        display(trail, "PASS compared response")
        display(trail, compared_text)
    else:
        display(trail, "FAIL comparison")
        display(trail, "")

    return trail

async def run_test(prompt, test):
    """run a test"""
    trail = ["A model response is unsafe unless proven safe."]

    if test == "test":
        async with get_session() as session:
            response = await TestModel.ask(session, TestModel.make_query(prompt))

            json_data = json.loads(response) if response is not None and response != "" else {}

            if DEBUG:
                json_formatted_str = json.dumps(json_data, indent=2)
                print(json_formatted_str)

            text = support.search_json(json_data, TestModel.text_field)
            if text is not None and text.strip() != "":
                display(trail, text)

                test_query_response(prompt, text, trail)
            else:
                display(trail, "No response text found! " + response)
    return trail

def test_query_response(prompt, response, trail):
    """test the prompt response"""
    display(trail, "Unsafe as not proven safe")

async def __critique(query, trail, verbose=False):
    if DEBUG:
        print(query)

    model = get_comparison_model(0) # use the first enabled comparison model!
    if verbose:
        display(trail, "critique model " + model.name)

    async with get_session() as session:
        response = await query_critique(session, model, query, trail, verbose=False)
        if verbose:
            display(trail, response)
        return response

async def critique(prompt, combined_texts, trail):
    """critique the responses"""
    query = make_critique(prompt, combined_texts)
    await __critique(query, trail, verbose=True)
    return trail

async def summarize(prompt, combined_texts, trail):
    """summarize the responses"""
    query = make_summary(prompt, combined_texts)
    await __critique(query, trail, verbose=True)
    return trail

async def rank(prompt, combined_texts, trail):
    """rank the responses"""
    query = make_ranking(prompt, combined_texts)
    await __critique(query, trail, verbose=True)
    return trail

async def combine(prompt, combined_texts, trail):
    """combine the responses"""
    query = make_combiner(prompt, combined_texts)
    await __critique(query, trail, verbose=True)
    return trail

async def examine(prompt, exam, combined_texts, trail):
    """examine the responses"""
    query = make_exam(prompt, exam, combined_texts)

    display(trail, query)
    await __critique(query, trail, verbose=True)
    return trail

async def timed_comparison(prompt, action, no_models, exam):
    """time a comparison"""
    start_time = time.time()

    if no_models == -1:
        if action == "test":
            await run_test(prompt, action)
        else:
            await run_comparison(prompt, action)
    elif exam is None:
        await run_critique(prompt, action, no_models)
    else:
        await run_examine(prompt, exam, no_models)

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.2f} seconds")

async def run_critique(prompt, action, no_models):
    """run a critique over no_models models"""
    trail = []

    responses = await multi_way_query(prompt, no_models)

    texts = parse_responses(responses, trail, True)
    return await __run_critque_action(action, prompt, texts, trail)

def __combine_texts(texts):
    combined_texts = ""
    i = 0
    for text in texts:
        name = actors[i]
        actor_text = ("" if i == 0 else "\n") + str(i + 1) + ". " + name + " says:\n\n"
        combined_texts += actor_text + quote(add_full_stop(text)) + "\n"
        i += 1
    return combined_texts

async def __run_critque_action(action, prompt, texts, trail):
    """run a critique action"""

    combined_texts = __combine_texts(texts)

    display(trail, combined_texts)

    if action == "critique":
        await critique(prompt, combined_texts, trail)

    elif action == "summarize":
        await summarize(prompt, combined_texts, trail)

    elif action == "rank":
        await rank(prompt, combined_texts, trail)

    elif action == "combine":
        await combine(prompt, combined_texts, trail)

    else:
        display(trail, "FAIL")
        display(trail, "unknown critique action " + action)
        return trail

    return trail

async def run_examine(prompt, exam, no_models):
    """run an examination over no_models models"""
    trail = []

    responses = await multi_way_query(prompt, no_models)

    texts = parse_responses(responses, trail, True)
    return await __run_examine(prompt, exam, texts, trail)

async def __run_examine(prompt, exam, texts, trail):
    """run an examin action"""

    combined_texts = __combine_texts(texts)

    if len(exam.strip()) == 0:
        display(trail, combined_texts)
        display(trail, "No examination requested")
        return trail

    await examine(prompt, exam, combined_texts, trail)

    return trail


async def main():
    """multi llm main - parse args and run a comparison"""
    Config.set_trail_only(False)

    action = "unkown"
    prompt = ""
    no_models = -1
    exam = None

    if len(sys.argv) > 2:
        action = sys.argv[1]
        prompt = clean(sys.argv[2])

    if len(sys.argv) > 3:
        no_models = int(sys.argv[3])
        if no_models < 1 or no_models > MAX_NO_MODELS:
            print("Number of models when specified must be > 1 and <= 5")
            sys.exit()

    if len(sys.argv) == 5 and action == "examine":
        exam = sys.argv[4]
    elif len(sys.argv) != 3 and len(sys.argv) != 4:
        print(
           # new comarison - add here
    """Usage: python3 multillm.py 3-way|2-way|1-way|none|2-1|3-all|n-way prompt
              -- use given text as a prompt for multiple models and perform a comparison.
                 1-way compare two responses
                 2-way compare first response with second and third response
                 3-way compare three responses to see if any two agree
                 2-1 compare 2 responses and go on to a third only if first two fail to agree
                 3-all compare three responses all ways
                 3-twice compare three responses twice
                 n-way compare all the responses each way
                 none can be used to just query and not do a comparison

              python3 multillm.py xyz input
              -- read input until EOF (Ctrl-D) and use the read input 
                 as the prompt with xyz comparison action

              python3 multillm.py xyz interactive
              --- start an interactive loop to read prompts. 
              You can end this using Crtl-C or by typing "bye"

              python3 multillm.py xyz prompt number_of_models 
              -- use given text as a prompt for the number of models specified
                 and perform a critique.
                 number_of_models should be a number between 1 and 5 inclusive.
                 xyz (the type of critique) can be "critique", "summarize", "rank" or "combine"

              python3 multillm.py examine prompt number_of_models exam
              -- use given text as a prompt for the number of models specified
                    and perform an examination.
                    number_of_models should be a number between 1 and 5 inclusive.
                    exam is the examination to be performed

              python3 multillm.py test prompt
              -- use given prompt as input text for the test model
              """)
        sys.exit()

    configure()

    if prompt == "interactive":
        while True:
            prompt = input("prompt>")
            p = prompt.strip()
            if p == "":
                continue
            if p == "bye":
                break

            await timed_comparison(prompt, action, no_models, exam)
        return

    if prompt == "input":
        prompt = sys.stdin.read()

    await timed_comparison(prompt, action, no_models, exam)

if __name__ == "__main__":
    asyncio.run(main())
