
statement_compare_instructions = "\nCompare their two statements and say YES if they are equivalent. Otherwise say NO." + \
                       " Make a functional comparison and ignore phrasing differences." + \
                       " Additional information provided by one statement does not matter unless it contracts the other statement."

answer_compare_instructions = "\nCompare their two answers and say YES if they agree. Otherwise say NO." + \
                       " Make a functional comparison and ignore phrasing differences." + \
                       " Additional information provided by one answer does not matter unless it contracts the other answer."


def make_statement_comparison(query, actor1, statement1, actor2, statement2):
    return "" + actor1 + " says:\n" + statement1 + "\n\n" + \
           actor2 + " says:\n" + statement2 + "\n" + \
           statement_compare_instructions

def make_answer_comparison(query, actor1, statement1, actor2, statement2):
    return "When " + actor1 + " and " + actor2 + " were asked the following:\n" + query + "\n\n" + actor1 + " says:\n" + statement1 + "\n\n" + \
           actor2 + " says:\n" + statement2 + "\n" + \
           answer_compare_instructions

make_comparison = make_answer_comparison
