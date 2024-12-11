import support 

llama_api_key = support.read_file_as_string("llama-api-key").strip()

model = "llama3.3-70b"
url = "https://api.llama-api.com/chat/completions"

def make_query(text):
  return  "{ \"model\": \"" + model + "\", \"messages\": [{\"role\": \"user\", \"content\": \"" + \
          text + "\"}]}"

async def ask(session, query):
  headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + llama_api_key
  }
  async with session.post(url, data=query.encode(), headers=headers) as response:
    print(f"Fetched {url}: Status code {response.status}")
    if response.status != 200:
      return "{\"error\": " + str(response.status) + "}"
    return await response.text()
    