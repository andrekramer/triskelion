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
        return await support.ask(URL, session, query, headers)

class Openai2(Openai):
    """openai 4o mini"""
    name = "openai2"
    model = "gpt-4o-mini"
