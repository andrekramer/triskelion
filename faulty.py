import support

class Faulty(support.Model):
  name = "faulty" 
  model = "guaranteed-to-fail"
  text_field = "text"
  response = "Sorry dave I'm afraid I can't do that."

  def make_query(text):
    return support.make_openai_std_query(text, Faulty.model)

  async def ask(session, query):
    if True:
      return "{\"error\": 500 }"
    else:
      return "{ text: \"" + response +"\"}"
  