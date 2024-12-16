import support 

openai_api_key = support.read_file_as_string("openai-api-key").strip()

url = "https://api.openai.com/v1/chat/completions"

class Openai(support.Model):
  name = "openai"
  model = "gpt-4o"
  text_field = "content"
 
  def make_query(text):
    return support.make_openai_std_query(text, Openai.model)

  async def ask(session, query):
    headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + openai_api_key
    }
    return await support.ask(url, session, query, headers)
