"""Agents as Plan,Validate,Act loops"""
from localhost import LocalHost
from openai import Openai
from claud import Claud
from gemini import Gemini2
from support import single_shot_ask, extract_tag

Agent = Openai
Checker = Claud
Actor = Gemini2

DEBUG = True

def make_plan(world, goal):
    """make a plan"""
    plan_prompt = f"Given a world with: <world>{world}</world>" + \
        f"\nPlan the following update <goal>{goal}</goal>" + \
        "\nOutput FINAL if no plan is possible or the plan in <plan></plan> tags."
    return plan_prompt

def make_validation(plan, world):
    "make a validation prompt"
    validate_prompt = f"Validate the following plan:\n <plan>{plan}</plan>" + \
            f"\nGiven a world with:\n <world>{world}</world>" + \
            "\n\nOuput PASS if the plan is valid or FAIL if not.\n" + \
            "\nYou must say one of these."
    return validate_prompt

def make_action(plan, world):
    """make an action to update the world"""
    act_prompt = f"Act on the following plan: <plan>{plan}</plan>" + \
            f"\nGiven a world with: <world>{world}</world>" + \
            "\nOutput the resulting world in <world></world> tags."
    return act_prompt

def observe(world):
    """observe the world"""
    world_content = extract_tag(world, "world")
    # here we would check the actual world state and return that
    return world_content

def log_error(message):
    """log an error message"""
    print(message)

async def run_agent(multillm, goal, world):
    """run an agent step """
    trail = ["Agent step"]
    if world is None:
        world = ""
    if goal is None:
        raise ValueError("No goal provided")

    multillm.display(trail, "plan")
    plan_prompt = make_plan(world, goal)
    multillm.display(trail, plan_prompt)

    async with multillm.get_session() as session:
        plan = await single_shot_ask(session, Agent, plan_prompt, allow_not_found=False)
        multillm.display(trail, plan)
        if plan.find("FINAL") != -1:
            multillm.display(trail, "Final state reached")
            return trail, plan, world, True

        plan = extract_tag(plan, "plan")
        if plan is None:
            msg = "No plan returned"
            log_error(msg)
            raise ValueError(msg)

        validate_prompt = make_validation(plan, world)
        multillm.display(trail, validate_prompt)

        validate_response = await single_shot_ask(session, Checker, validate_prompt)
        multillm.display(trail, validate_response)
        if validate_response.find("PASS") == -1 or validate_response.find("FAIL") != -1:
            multillm.display(trail, "Plan is invalid")
            log_error(f"Plan validation failed: {validate_response}")
            # No valid change to make so return the same world
            return trail, goal, world, False

        act_prompt = make_action(plan, world)
        multillm.display(trail, act_prompt)
        world2 = await single_shot_ask(session, Actor, act_prompt)
        multillm.display(trail, world2)

    world = observe(world2)
    if world2 is None:
        msg = "No world returned"
        log_error(msg)
        raise ValueError(msg)

    return trail, plan, world, False
