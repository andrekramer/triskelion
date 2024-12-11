import support

gemini_api_key = support.read_file_as_string("gemini-api-key").strip()

model = "gemini-1.5-flash-latest"
url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + gemini_api_key

def make_query(text):
  return "{\"contents\":[{\"parts\":[{\"text\":\"" + text + "\"}]}]}"

async def ask(session, query):
  headers = {
    "Content-Type": "application/json"
  }
  async with session.post(url, data=query.encode(), headers=headers) as response:
    print(f"Fetched {url}: Status code {response.status}")
    if response.status != 200:
      return "{\"error\": " + str(response.status) + "}"
    return await response.text()
    
