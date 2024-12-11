import support 

openai_api_key = support.read_file_as_string("openai-api-key").strip()

model = "gpt-4o"
url = "https://api.openai.com/v1/chat/completions"

def make_query(text):
  return  "{ \"model\": \"" + model + "\", \"messages\": [{\"role\": \"user\", \"content\": \"" + \
          text + "\"}]}"

async def ask(session, query):
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + openai_api_key
  }
  async with session.post(url, data=query.encode(), headers=headers) as response:
    print(f"Fetched {url}: Status code {response.status}")
    return await response.text()
    
