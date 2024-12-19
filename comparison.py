
compare_instructions = "\nCompare their two statements and say YES if they are equivalent. Otherwise say NO." + \
                       " Make a functional comparison and ignore phrasing differences." + \
                       " Additional information provided by one statement does not matter unless it contracts the other statement."

def make_comparison(query, actor1, statement1, actor2, statement2):
    return "" + actor1 + " says:\n" + statement1 + "\n\n" + \
           actor2 + " says:\n" + statement2 + "\n" + \
           compare_instructions
