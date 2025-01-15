"""template for new models/vedors"""
import support

# Add a api key file for model (if required)
api_key = support.read_file_as_string("new-model-api-key").strip()

# Add a url for the new model
URL = "https://"

# new model? copy this template
class NewModel(support.Model):
    """New model template"""
    name = "new-model"
    model = "new-model-version-string"
    text_field = "json-field-text-or-content-name"

    @classmethod
    def make_query(cls, text):
        """example make query method"""
        # you may be able to use openai queries:
        # return support.make_openai_std_query(text, cls.model)
        return ""

    @staticmethod
    async def ask(session, query):
        """example query method"""
        # Add headers as needed (note: this example uses standard "bearer" authentication)
        headers = {
         "Content-Type": "application/json",
         "Authorization": "Bearer " + api_key
        }
        # You will probably be able to use the ask method from support module:
        # return await support.ask(url, session, query, headers)

        return "{ \"error\": \"TO DO ADD MODEL IMPL\"}"

# example of a new model
class NewModel2(NewModel):
    """New model 2 template"""
    name = "new-model2"
    model = "new-model2-version-string"
