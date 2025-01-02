import json

class Model:
    """Base class for all AI models"""
    def make_query(text): raise RuntimeError("Not implemented")
    async def ask(session, query): raise RuntimeError("Not implemented")
    # fields to implement: name, model, text_field
    pass

def serialize(json_object):
  return json.dumps(json_object)

def make_openai_std_query_with_str_concat(text, model):
  return  "{ \"model\": \"" + model + "\", \"messages\": [{\"role\": \"user\", \"content\": \"" + \
          text + "\"}]}"

def make_openai_std_query_from_obj(text, model):
  obj = { "model": model }
  message = { "role": "user" }
  message["content"] = text
  messages = []
  messages.append(message)
  obj["messages"] = messages

  return serialize(obj)

make_openai_std_query = make_openai_std_query_from_obj

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
  try:
    async with session.post(url, data=query.encode(), headers=headers) as response:
      print(f"Fetched {url}: Status code {response.status}")
      if response.status != 200:
        return "{\"error\": " + str(response.status) + "}"
      return await response.text()
  except Exception as e:
    return "{ \"error\": \"" + e.__class__.__name__ + "\"}"

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
