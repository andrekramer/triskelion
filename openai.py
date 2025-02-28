"""Openai models"""
import support

openai_api_key = support.read_file_as_string("openai-api-key").strip()

URL = "https://api.openai.com/v1/chat/completions"

class Openai(support.Model):
    """Openai gtp-4o"""
    name = "openai"
    model = "gpt-4o"
    text_field = "content"

    @classmethod
    def make_query(cls, text):
        """make a query for openai model"""
        return support.make_openai_std_query(text, cls.model)

    @staticmethod
    async def ask(session, query):
        """make a request using http to openai"""
        headers = {
          "Content-Type": "application/json",
          "Authorization": "Bearer " + openai_api_key
        }
        # print(f"openai ask: {query}")
        return await support.ask(URL, session, query, headers)

class Openai2(Openai):
    """openai o1 mini"""
    name = "openai2"
    model = "o1-mini"

class Openai3(Openai):
    """openai o3 mini"""
    name = "openai3"
    model = "o3-mini"

class Openai4(Openai):
    """gpt-4.5-preview"""
    name = "openai4"
    model = "gpt-4.5-preview"
