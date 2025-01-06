"""Claud AI Model"""
import support

claud_api_key = support.read_file_as_string("claud-api-key").strip()

URL = "https://api.anthropic.com/v1/messages"

class Claud(support.Model):
    """Claud AI Model"""
    name = "claud"
    model = "claude-3-5-sonnet-20241022"
    text_field = "text"

    @staticmethod
    def make_query(text):
        """make claud query"""
        obj = { "model": Claud.model, "max_tokens": 2048 }
        return support.make_std_query_from_object(obj, text)

    @staticmethod
    async def ask(session, query):
        """perform query"""
        headers = {
          "Content-Type": "application/json",
          "x-api-key": claud_api_key,
          "anthropic-version": "2023-06-01"
        }
        return await support.ask(URL, session, query, headers)
