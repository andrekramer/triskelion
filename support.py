
def make_openai_std_query(text, model):
  return  "{ \"model\": \"" + model + "\", \"messages\": [{\"role\": \"user\", \"content\": \"" + \
          text + "\"}]}"

def read_file_as_string(filepath):
    try:
        with open(filepath, 'r') as file:
            file_content = file.read()
        return file_content
    except FileNotFoundError:
        print(f"Error: File '{filepath}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading '{filepath}': {e}")
        return None
    
async def ask(url, session, query, headers):
  async with session.post(url, data=query.encode(), headers=headers) as response:
    print(f"Fetched {url}: Status code {response.status}")
    if response.status != 200:
      return "{\"error\": " + str(response.status) + "}"
    return await response.text()

def search_json(json_data, target_key):
    """Recursively searches a JSON object for a key."""
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            if key == target_key:
                return value
            elif isinstance(value, (dict, list)):  # Recurse into nested structures
                result = search_json(value, target_key)
                if result is not None:
                    return result
    elif isinstance(json_data, list):
        for item in json_data:
            if isinstance(item, (dict, list)):
                result = search_json(item, target_key)
                if result is not None:
                    return result
    return None  # Key not found
