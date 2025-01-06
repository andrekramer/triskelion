"""Simulate a faulty model"""
import support

class Faulty(support.Model):
    """A Faulty Model"""
    name = "faulty"
    model = "guaranteed-to-fail"
    text_field = "text"
    response = "Sorry dave I'm afraid I can't do that."

    @staticmethod
    def make_query(text):
        """make a query for Faulty model"""
        return support.make_openai_std_query(text, Faulty.model)

    @staticmethod
    async def ask(session, query):
        """make a query to Faulty model"""
        if True:
            return "{\"error\": 500 }"
        return "{ text: \"" + Faulty.response +"\"}"
