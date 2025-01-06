"""Gemini models from Meta"""
import support

gemini_api_key = support.read_file_as_string("gemini-api-key").strip()

class Gemini(support.Model):
    """Meta Geminin 1.5 flast latest"""
    name = "gemini"
    model = "gemini-1.5-flash-latest"
    text_field = "text"

    @staticmethod
    def make_query(text):
        """make a query"""
        obj = {}
        part = { "text": text }
        contents = []
        parts = []
        parts.append(part)
        contents.append({ "parts": parts })
        obj["contents"] = contents
        return support.serialize(obj)

    @staticmethod
    async def ask(session, query):
        """make a request using http post"""
        url = "https://generativelanguage.googleapis.com/v1beta/models/" + \
              Gemini.model + ":generateContent?key=" + gemini_api_key
        headers = {
            "Content-Type": "application/json"
        }
        return await support.ask(url, session, query, headers)


class Gemini2(Gemini):
    """Meta Gemini 2.0 flash experimental"""
    name = "gemini2"
    model = "gemini-2.0-flash-exp"
