import support

hugface_api_key = support.read_file_as_string("hugface-api-key").strip()

base_url = "https://api-inference.huggingface.co/models"

class HugFace(support.Model):
  name = "hugface"
  model = "google/gemma-2-2b-it"
  text_field = "content"

  def make_query(text):
    return support.make_openai_std_query(text, HugFace.model)

  async def ask(session, query):
    url = base_url + "/" + HugFace.model + "/v1/chat/completions"
    print(url)
    headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + hugface_api_key
    }
    return await support.ask(url, session, query, headers)

class HugFace2(HugFace):
  name = "hugface2"
  model = "microsoft/Phi-3-mini-4k-instruct"

class HugFace3(HugFace2):
  name = "hugface3"
  model = "Qwen/Qwen2.5-7B-Instruct"
