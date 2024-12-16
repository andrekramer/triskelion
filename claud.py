import support 

claud_api_key = support.read_file_as_string("claud-api-key").strip()

url = "https://api.anthropic.com/v1/messages"

class Claud(support.Model):
  name = "claud"
  model = "claude-3-5-sonnet-20241022"
  text_field = "text"

  def make_query(text):
    return "{ \"model\": \"" + Claud.model + "\", \"max_tokens\": 1024, \"messages\": [{\"role\": \"user\", \"content\": \"" + \
          text + "\"} ]}"

  async def ask(session, query):
    headers = {
      "Content-Type": "application/json",
      "x-api-key": claud_api_key,
      "anthropic-version": "2023-06-01"
    }
    return await support.ask(url, session, query, headers)

