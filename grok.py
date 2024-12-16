import support 

grok_api_key = support.read_file_as_string("grok-api-key").strip()

url = "https://api.x.ai/v1/chat/completions"

class Grok(support.Model):
 name = "grok"
 model = "grok-beta"
 text_field = "content"

 def make_query(text):
   return support.make_openai_std_query(text, Grok.model)

 async def ask(session, query):
   headers = {
     "Content-Type": "application/json",
     "Authorization": "Bearer " + grok_api_key
   }
   return await support.ask(url, session, query, headers)
