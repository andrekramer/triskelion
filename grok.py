import support 

grok_api_key = support.read_file_as_string("grok-api-key").strip()

url = "https://api.x.ai/v1/chat/completions"

model = "grok-beta"

def make_query(text):
  return  "{ \"model\": \"" + model + "\", \"messages\": [{\"role\": \"user\", \"content\": \"" + \
          text + "\"}]}"

async def ask(session, query):
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + grok_api_key
  }
  async with session.post(url, data=query.encode(), headers=headers) as response:
    print(f"Fetched {url}: Status code {response.status}")
    if response.status != 200:
      return "{\"error\": " + str(response.status) + "}"
    return await response.text()
