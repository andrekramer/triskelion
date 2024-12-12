import support 

llama_api_key = support.read_file_as_string("llama-api-key").strip()

model = "llama3.3-70b"
url = "https://api.llama-api.com/chat/completions"

def make_query(text):
  return support.make_openai_std_query(text, model)

async def ask(session, query):
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + llama_api_key
  }
  return await support.ask(url, session, query, headers)
    