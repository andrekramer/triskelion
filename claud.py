import support 

claud_api_key = support.read_file_as_string("claud-api-key").strip()

url = "https://api.anthropic.com/v1/messages"

def make_query(text):
  return "{ \"model\": \"claude-3-5-sonnet-20241022\", \"max_tokens\": 1024, \"messages\": [{\"role\": \"user\", \"content\": \"" + \
         text + "\"} ]}"

async def ask(session, query):
  headers = {
    "Content-Type": "application/json",
    "x-api-key": claud_api_key,
    "anthropic-version": "2023-06-01"
  }
  async with session.post(url, data=query.encode(), headers=headers) as response:
    print(f"Fetched {url}: Status code {response.status}")
    if response.status != 200:
      return "{\"error\": " + str(response.status) + "}"
    return await response.text()

