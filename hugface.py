"""Various models hosted by hugging face"""
import support

hugface_api_key = support.read_file_as_string("hugface-api-key").strip()

URL = "https://api-inference.huggingface.co/models"

class HugFace(support.Model):
    """Gemma 2"""
    name = "hugface"
    model = "google/gemma-2-2b-it"
    text_field = "content"

    @staticmethod
    def make_query(text):
        """make a query for hugging face"""
        return support.make_openai_std_query(text, HugFace.model)

    @staticmethod
    async def ask(session, query):
        """make a request to model hosted on hugging face"""
        url = URL + "/" + HugFace.model + "/v1/chat/completions"
        print(url)
        headers = {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + hugface_api_key
        }
        return await support.ask(url, session, query, headers)

class HugFace2(HugFace):
    """Microsoft Phi mini 4k instruct"""
    name = "hugface2"
    model = "microsoft/Phi-3-mini-4k-instruct"

class HugFace3(HugFace2):
    """Qwen Qwen 2.5"""
    name = "hugface3"
    model = "Qwen/Qwen2.5-7B-Instruct"
