

from gemini import Gemini
from claud import  Claud
from openai import Openai
from grok import Grok
from llama import Llama

# The models and order of responses (skiping any not in schedule). Need at least 3 different models for 3 way comparisons.
models = [Gemini, Claud, Openai, Grok, Llama]

comparison_models = [Gemini, Llama, Openai] # Need 3 models for 3-way. They can be the same model applied more than once.

# Which models to query
schedule = {
  "gemini": True,
  "claud": False,
  "openai": True,
  "grok": False,
  "llama": True
}

# model versions to use for queries
model_versions = {
  "gemini": "gemini-1.5-flash-latest",
  "claud": "claude-3-5-sonnet-20241022",
  "openai": "gpt-4o",
  "grok": "grok-beta",
  "llama":  "llama3.3-70b"
}

compare_instructions = "\nCompare their two statements and say YES if they are equivalent. Otherwise say NO." + \
                       " Make a functional comparison and ignore phrasing differences."


def configure():
  # Push down the model configuration to imported models
  Gemini.model = model_versions["gemini"]
  Claud.model = model_versions["claud"]
  Openai.model = model_versions["openai"]
  Grok.model = model_versions["grok"]
  Llama.model = model_versions["llama"]
