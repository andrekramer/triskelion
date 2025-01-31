
"""Comparison prompts"""

from config import Config

STATEMENT_COMPARE_INSTRUCTIONS = \
    "\nCompare their two statements and say YES if they are equivalent." + \
    " Otherwise say NO before any explanations." + \
    " Make a functional comparison and ignore phrasing differences." + \
    " Additional information provided by one statement does not matter unless" + \
    " it contracts the other statement."

ANSWER_COMPARE_INSTRUCTIONS = \
    "\nCompare their two answers and say YES if they agree before any explanation." + \
    " Otherwise say NO before any explanation." + \
    " Make a functional comparison and ignore phrasing differences." + \
    " Additional information provided by one answer does not matter unless" + \
    " it contradicts the other answer."

JUSTIFY_INSTRUCTIONS = \
    "\nJustify your answer by explaining why " + \
    "you think the two statements or answers are equivalent or not."

def __get_justify_instructions():
    return JUSTIFY_INSTRUCTIONS if Config.get_justify() else ""

def add_full_stop(s):
    """add a full stop at end of string"""
    s = s.strip()
    if s.endswith(".") or s.endswith("?") or s.endswith("!"):
        return s
    return s + "."

def quote(s):
    """quote a reponse"""
    # return s
    #return "<response>" + s + "</response>"
    return "<quote>" + s + "</quote>"

def make_statement_comparison(actor1, statement1, actor2, statement2):
    """make a statement comparison style prompt"""
    if statement1.strip() == "" or statement2.strip() == "":
        return ""
    return actor1 + " and " + actor2 + " make two statements.\n" + \
           actor1 + " says:\n" + quote(add_full_stop(statement1)) + "\n\n" + \
           actor2 + " says:\n" + quote(add_full_stop(statement2)) + "\n" + \
           STATEMENT_COMPARE_INSTRUCTIONS + __get_justify_instructions()

def make_answer_comparison(query, actor1, answer1, actor2, answer2):
    """make an answer comparison style prompt"""
    if answer1.strip() == "" or answer2.strip() == "":
        return ""
    return "When " + actor1 + " and " + actor2 + " were asked the following:\n" + \
           quote(query) + "\n\n" + actor1 + \
           " answered:\n" + quote(add_full_stop(answer1)) + "\n\n" + \
           actor2 + " answered:\n" + quote(add_full_stop(answer2)) + "\n" + \
           ANSWER_COMPARE_INSTRUCTIONS + __get_justify_instructions()


def make_comparison(query, actor1, statement1, actor2, statement2):
    """make a comparison promp based on the config"""
    if Config.include_query:
        return make_answer_comparison(query, actor1, statement1, actor2, statement2)

    return make_statement_comparison(actor1, statement1, actor2, statement2)

def make_critique(query, statements):
    """make a critique prompt"""
    if Config.include_query:
        critique = "Critique the following answers to this query:\n\n" + \
            quote(query) + "\n\n"
    else:
        critique = "Critique the following statements.\n\n"
    return critique + statements

def make_summary(query, statements):
    """make a summary prompt"""
    if Config.include_query:
        summarize = "Summarize the following answers to this query:\n\n" + \
            quote(query) + "\n\n"
    else:
        summarize = "Summarize the following statements.\n\n"
    return summarize + statements

def make_ranking(query, statements):
    """make a ranking prompt"""
    if Config.include_query:
        rank = "Rank the following answers to this query:\n\n" + \
            quote(query) + "\n\n"
    else:
        rank = "Rank the following statements.\n\n"
    return rank + statements

def make_combiner(query, statements):
    """make a combiner prompt"""
    if Config.include_query:
        combiner = "Combine the following answers to this query into a concensus opinion:\n\n" + \
            quote(query) + "\n\n"
    else:
        combiner = "Combine the following statements into a concensus opinion.\n\n"
    return combiner + statements

def make_exam(query, exam, statements):
    """make an examine prompt"""
    if Config.include_query:
        examine = "The following are answers to this query:\n\n" + \
            quote(query) + "\n\n"
    else:
        examine = "The following are different statements made.\n\n"
    return examine + statements + "\n\n" + exam
