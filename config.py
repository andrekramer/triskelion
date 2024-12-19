from gemini import Gemini
from claud import  Claud
from openai import Openai, Openai2
from grok import Grok
from llama import Llama, Llama2

# The models and order of responses (skiping any not in schedule). Need at least 3 different models for 3 way comparisons.
models = [Gemini, Claud, Openai, Openai2, Grok, Llama, Llama2]

comparison_models = [Gemini, Llama, Openai] # Need at least 3 models for 3-way. They can be the same model applied more than once.

# Which models to query
schedule = {
  "gemini": True,
  "claud": False,
  "openai": True,
  "openai2": False,
  "grok": False,
  "llama": True,
  "llama2": False
}

# model versions to use for queries
model_versions = {
  "gemini": "gemini-1.5-flash-latest",
  "claud": "claude-3-5-sonnet-20241022",
  "openai": "gpt-4o",
  "openai2": "chatgpt-4o-latest",
  "grok": "grok-beta",
  "llama": "llama3.2-3b",
  "llama2":  "llama3.3-70b"
}

def configure():
  # Push down the model configuration to imported models
  Gemini.model = model_versions["gemini"]
  Claud.model = model_versions["claud"]
  Openai.model = model_versions["openai"]
  Openai2.model = model_versions["openai2"]
  Grok.model = model_versions["grok"]
  Llama.model = model_versions["llama"]
  Llama2.model = model_versions["llama2"]

