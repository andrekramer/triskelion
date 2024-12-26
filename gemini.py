import support

gemini_api_key = support.read_file_as_string("gemini-api-key").strip()

class Gemini(support.Model):
  name = "gemini"
  model = "gemini-1.5-flash-latest"
  text_field = "text"

  def make_query_str(text):
    return "{\"contents\":[{\"parts\":[{\"text\":\"" + text + "\"}]}]}"

  def make_query(text):
    obj = {}
    part = { "text": text }
    contents = []
    parts = []
    parts.append(part)
    contents.append({ "parts": parts })
    obj["contents"] = contents
    return support.serialize(obj)
  
  async def ask(session, query):
    url = "https://generativelanguage.googleapis.com/v1beta/models/" + Gemini.model + ":generateContent?key=" + gemini_api_key
    headers = {
        "Content-Type": "application/json"
    }
    return await support.ask(url, session, query, headers)
  

class Gemini2(Gemini):
  name = "gemini2"
  model = "gemini-2.0-flash-exp"
