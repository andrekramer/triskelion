
"""Comparison prompts"""

STATEMENT_COMPARE_INSTRUCTIONS = \
    "\nCompare their two statements and say YES if they are equivalent." + \
    " Otherwise say NO." + \
    " Make a functional comparison and ignore phrasing differences." + \
    " Additional information provided by one statement does not matter unless" + \
    " it contracts the other statement."

ANSWER_COMPARE_INSTRUCTIONS = \
    "\nCompare their two answers and say YES if they agree before any explanation." + \
    " Otherwise say NO before any explanation." + \
    " Make a functional comparison and ignore phrasing differences." + \
    " Additional information provided by one answer does not matter unless" + \
    " it contradicts the other answer."

def add_full_stop(s):
    """add a full stop at end of string"""
    if s.strip().endswith("."):
        return s
    return s + "."

def make_statement_comparison(query, actor1, statement1, actor2, statement2):
    """make a statement comparison style prompt"""
    if statement1.strip() == "" or statement2.strip() == "":
        return ""
    return "" + actor1 + " says:\n" + add_full_stop(statement1) + "\n\n" + \
           actor2 + " says:\n" + add_full_stop(statement2) + "\n" + \
           STATEMENT_COMPARE_INSTRUCTIONS

def make_answer_comparison(query, actor1, answer1, actor2, answer2):
    """make an answer comparison style prompt"""
    if answer1.strip() == "" or answer2.strip() == "":
        return ""
    return "When " + actor1 + " and " + actor2 + " were asked the following:\n" + \
           add_full_stop(query) + "\n\n" + actor1 + \
           " answered:\n" + add_full_stop(answer1) + "\n\n" + \
           actor2 + " answered:\n" + add_full_stop(answer2) + "\n" + \
           ANSWER_COMPARE_INSTRUCTIONS

# Configure the type of comparison to make:

make_comparison = make_answer_comparison
