"""critique and examine models"""

from config import DEBUG, get_comparison_model, actors
from comparison import add_full_stop, quote
from comparison import make_exam, make_critique, make_summary, make_ranking, make_combiner


async def run_critique(multillm, prompt, action, no_models):
    """run a critique over no_models models"""
    trail = []

    responses = await multillm.multi_way(prompt, no_models)

    texts = multillm.parse(responses, trail, True)
    return await __run_critque_action(multillm, action, prompt, texts, trail)

def __combine_texts(texts):
    combined_texts = ""
    i = 0
    for text in texts:
        name = actors[i]
        actor_text = ("" if i == 0 else "\n") + str(i + 1) + ". " + name + " says:\n\n"
        combined_texts += actor_text + quote(add_full_stop(text)) + "\n"
        i += 1
    return combined_texts

async def run_examine(multillm, prompt, exam, no_models, parallel=False):
    """run an examination over no_models models"""
    trail = []

    if parallel:
        responses = await multillm.multi_way_parallel(prompt, no_models)
        texts = multillm.parse_parallel(responses, trail, True)
    else:
        responses = await multillm.multi_way(prompt, no_models)
        texts = multillm.parse(responses, trail, True)

    return await __run_examine(multillm, prompt, exam, texts, trail)

async def __run_examine(multillm, prompt, exam, texts, trail):
    """run an examin action"""
    combined_texts = __combine_texts(texts)

    if len(exam.strip()) == 0:
        multillm.display(trail, combined_texts)
        multillm.display(trail, "No examination requested")
        return trail

    await examine(multillm, prompt, exam, combined_texts, trail)

    return trail

async def examine(multillm, prompt, exam, combined_texts, trail):
    """examine the responses"""
    query = make_exam(prompt, exam, combined_texts)

    multillm.display(trail, query)
    await __critique(multillm, query, trail, verbose=True)
    return trail

async def __run_critque_action(multillm, action, prompt, texts, trail):
    """run a critique action"""

    combined_texts = __combine_texts(texts)

    multillm.display(trail, combined_texts)

    if action == "critique":
        await critique(multillm, prompt, combined_texts, trail)

    elif action == "summarize":
        await summarize(multillm, prompt, combined_texts, trail)

    elif action == "rank":
        await rank(multillm, prompt, combined_texts, trail)

    elif action == "combine":
        await combine(multillm, prompt, combined_texts, trail)

    else:
        multillm.display(trail, "FAIL")
        multillm.display(trail, "unknown critique action " + action)
        return trail

    return trail

async def __critique(multillm, query, trail, verbose=False):
    if DEBUG:
        print(query)

    model = get_comparison_model(0) # use the first enabled comparison model!
    if verbose:
        multillm.display(trail, "critique model " + model.name)

    async with multillm.get_session() as session:
        response = await multillm.query_critique(session, model, query, trail, verbose=False)
        if verbose:
            multillm.display(trail, response)
        return response

async def critique(multillm, prompt, combined_texts, trail):
    """critique the responses"""
    query = make_critique(prompt, combined_texts)
    await __critique(multillm, query, trail, verbose=True)
    return trail

async def summarize(multillm, prompt, combined_texts, trail):
    """summarize the responses"""
    query = make_summary(prompt, combined_texts)
    await __critique(multillm, query, trail, verbose=True)
    return trail

async def rank(multillm, prompt, combined_texts, trail):
    """rank the responses"""
    query = make_ranking(prompt, combined_texts)
    await __critique(multillm, query, trail, verbose=True)
    return trail

async def combine(multillm, prompt, combined_texts, trail):
    """combine the responses"""
    query = make_combiner(prompt, combined_texts)
    await __critique(multillm, query, trail, verbose=True)
    return trail
