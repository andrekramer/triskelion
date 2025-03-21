"""Triskelion Flask Web App"""
# partly generated by Gemini AI
from flask import Flask, request, render_template, jsonify

from multillm import multillm, multillm_agent, \
    run_comparison, run_critique, run_examine, \
    run_test
from config import configure, MAX_NO_MODELS, DEFAULT_NO_MODELS, \
    web_comparisons, default_web_comparison, \
    web_critiques, default_web_critique, \
    web_tests, default_web_test
from config import schedule, comparison_schedule
from config import models, comparison_models, Config
from agent import run_agent

configure()
DEV = True

app = Flask(__name__)


@app.route('/prompt', methods=['POST'])
async def prompt_comparison():
    """prompt web methdd"""
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({"error": "Invalid request: 'prompt' field is required."}), 400

        prompt = data['prompt']
        action = data.get("action", "3-way")
        trail = await run_comparison(prompt, action)

        response_text = trail[-1]
        response = {"compared_response": response_text}
        return jsonify(response), 200

    except Exception as e:
        return jsonify({"error": f"Error processing the prompt: {str(e)}"}), 500


@app.route("/", methods=["GET", "POST"])
async def index():
    """default web method"""
    return render_template("index.html")

@app.route("/compare", methods=["GET", "POST"])
async def compare():
    """compare web method"""
    if request.method == "POST":
        prompt_text = request.form["text_prompt"]
        selected_comp = request.form.get("comp", str(default_web_comparison))
        print("selected comp " + selected_comp)

        if prompt_text is None or prompt_text.strip() == "":
            return render_template("compare.html",
                                   selected_comp=selected_comp, comps=web_comparisons)

        response_lines = await process_comparison(prompt_text, selected_comp)

        return render_template("compare.html",
                               response=response_lines,
                               prompt=prompt_text,
                               selected_comp=selected_comp,
                               comps=web_comparisons) # Render the HTML page

    return render_template("compare.html",
                           selected_comp=str(default_web_comparison),
                           comps=web_comparisons) # renders the page on a GET request

@app.route("/critique", methods=["GET", "POST"])
async def critique():
    """citique web method"""
    if request.method == "POST":
        prompt_text = request.form["text_prompt"]
        no_models = int(request.form.get("no_models", str(DEFAULT_NO_MODELS)))

        selected_critique = request.form.get("critique", str(default_web_critique))
        print("selected critique " + selected_critique)

        if prompt_text is None or prompt_text.strip() == "" or \
            no_models < 1 or no_models > MAX_NO_MODELS:
            if no_models < 1 or no_models > MAX_NO_MODELS:
                no_models = DEFAULT_NO_MODELS

            return render_template("critique.html",
                                   no_models=no_models,
                                   selected_critique=selected_critique,
                                   critiques=web_critiques)

        response_lines = await process_critique(prompt_text, selected_critique, no_models)

        return render_template("critique.html",
                               no_models=no_models,
                               response=response_lines,
                               prompt=prompt_text,
                               selected_critique=selected_critique,
                               critiques=web_critiques)

    return render_template("critique.html",
                           no_models=DEFAULT_NO_MODELS,
                           selected_critique=str(default_web_critique),
                           critiques=web_critiques)

@app.route("/examine", methods=["GET", "POST"])
async def inspect():
    """examine web method"""
    if request.method == "POST":
        prompt_text = request.form["text_prompt"]
        exam_text = request.form["text_exam"]
        parallel = request.form.get("parallel", False)
        print("parallel " + str(parallel))
        no_models = int(request.form.get("no_models", str(DEFAULT_NO_MODELS)))

        if prompt_text is None or prompt_text.strip() == "" or \
            no_models < 1 or no_models > MAX_NO_MODELS:
            if no_models < 1 or no_models > MAX_NO_MODELS:
                no_models = DEFAULT_NO_MODELS

            return render_template("examine.html",
                                   no_models=no_models,
                                   parallel=parallel)

        response_lines = await process_examine(prompt_text, exam_text, no_models, parallel)

        return render_template("examine.html",
                               no_models=no_models,
                               parallel=parallel,
                               response=response_lines,
                               prompt=prompt_text,
                               exam=exam_text)

    return render_template("examine.html",
                           no_models=DEFAULT_NO_MODELS)

@app.route("/agent", methods=["GET", "POST"])
async def agent():
    """agent web method"""
    if request.method == "POST":
        world_text = request.form["world_prompt"]
        goal_text = request.form["goal_prompt"]

        if goal_text is None or goal_text.strip() == "":
            return render_template("agent.html")

        response_lines, plan, world, done = await process_agent(goal_text, world_text)

        return render_template("agent.html",
                               response=response_lines,
                               goal=goal_text,
                               world=world)

    return render_template("agent.html")

@app.route("/test", methods=["GET", "POST"])
async def test():
    """test web method"""
    if request.method == "POST":
        prompt_text = request.form["text_prompt"]
        selected_test = request.form.get("test", str(default_web_test))
        print("selected test " + selected_test)

        if prompt_text is None or prompt_text.strip() == "":
            return render_template("test.html",
                                   selected_test=selected_test,
                                   tests=web_tests)

        response_lines = await process_test(prompt_text, selected_test)

        return render_template("test.html",
                               response=response_lines,
                               prompt=prompt_text,
                               selected_test=selected_test,
                               tests=web_tests) # Render the HTML page

    return render_template("test.html",
                           selected_test=str(default_web_test),
                           tests=web_tests)

@app.route('/config', methods=['GET', 'POST'])
def configure_comparison():
    """configure web method"""
    feature_sets, selected_options = get_features()

    if request.method == 'POST':
        selected_options = request.form.getlist('selected_options')
        # Process the selected checkboxes

        print(f"Selected Options: {selected_options}")

        config_models(selected_options)

        Config.set_single_comparator("single-compare" in selected_options)
        Config.set_diff_comparator("diff-comparisons" in selected_options)
        Config.set_justify("justify" in selected_options)
        Config.set_include_query("comapre_answers" in selected_options)

        return jsonify(selected_options)

    return render_template('config.html',
                           feature_sets=feature_sets,
                           selected_options=selected_options)

def get_features():
    """get feature settings"""
    feature_sets = {
        "set_models": {
            "name": "Models",
            "options": []
        },
        "set_comparison_models": {
            "name": "Comparison Models",
            "options": []
        },
        "others": {
           "name": "Others",
           "options": []
        }
    }

    selected_options = [""]
    options = []
    for model in models:
        if not model.name in schedule:
            continue
        if schedule[model.name]:
            selected_options.append("model-" + model.name)
        options.append({
           "name": model.name,
           "id": "model-" + model.name,
           "version": model.model
        })
    feature_sets["set_models"]["options"] = options

    options = []
    for model in comparison_models:
        if not model.name in comparison_schedule:
            continue
        if comparison_schedule[model.name]:
            selected_options.append("comparison-model-" + model.name)
        options.append({
           "name": model.name,
           "id": "comparison-model-" + model.name,
           "version": model.model
        })
    feature_sets["set_comparison_models"]["options"] = options

    options = []
    if Config.get_single_comparator():
        selected_options.append("single-compare")
    if Config.get_diff_comparator():
        selected_options.append("diff-comparisons")
    if Config.get_justify():
        selected_options.append("justify")
    if Config.get_include_query():
        selected_options.append("compare_answers")

    options.append({
       "name": "use first model for all comparisons",
        "id": "single-compare"
    })
    options.append({
       "name": "or use different model for comparisons or each in turn.",
        "id": "diff-comparisons"
    })
    options.append({
        "name": "justify comparisons",
        "id": "justify"
    })
    options.append({
        "name": "include query in comparison prompts",
        "id": "compare_answers"
    })

    feature_sets["others"]["options"] = options

    return (feature_sets, selected_options)

def config_models(selected_options):
    """configure models"""
    schedule2 = {}
    for m in schedule:
        schedule2[m] = False
    comparison_schedule2 = {}
    for cm in comparison_schedule:
        comparison_schedule2[cm] = False

    for option in selected_options:
        if option.startswith("model-"):
            m = option[6:]
            print("selected model " + m)
            schedule2[m] = True
        elif option.startswith("comparison-model-"):
            cm = option[17:]
            print("selected comparison model " + cm)
            comparison_schedule2[cm] = True

    for k,v in schedule2.items():
        schedule[k] = v
    for k,v in comparison_schedule2.items():
        comparison_schedule[k] = v

async def process_comparison(prompt, selected_comp):
    """process the prompt by running a comparison"""
    try:
        i = int(selected_comp)
        selected_comp = web_comparisons[i]

        result = await run_comparison(prompt, selected_comp) # respond with a list of strings
        return result
    except Exception as e:
        return ["failed to run comparison " + selected_comp, str(e)]

async def process_critique(prompt, selected_critique, no_models):
    """process the prompt by running a critique"""
    try:
        i = int(selected_critique)
        selected_critique = web_critiques[i]

        result = await run_critique(multillm, prompt, selected_critique, no_models)
        return result
    except Exception as e:
        return ["failed to run " + selected_critique, str(e)]

async def process_examine(prompt, exam, no_models, parallel):
    """process the prompt by running an examination"""
    try:
        result = await run_examine(multillm, prompt, exam, no_models, parallel)
        return result
    except Exception as e:
        return ["failed to run examine", str(e)]

async def process_test(prompt, selected_test):
    """process the prompt by running a test"""
    try:
        i = int(selected_test)
        selected_test = web_tests[i]

        result = await run_test(prompt, selected_test)
        return result
    except Exception as e:
        return ["failed to run test " + selected_test, str(e)]

async def process_agent(goal, world):
    """process the agent prompt by itterating the world"""
    try:
        result = await run_agent(multillm_agent, goal, world)
        return result
    except Exception as e:
        return ["failed to run agent", str(e)], "", world

if __name__ == "__main__":
    Config.set_trail_only(DEV)
    app.run(debug=DEV)
