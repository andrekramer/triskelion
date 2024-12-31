import os

if not os.path.isfile("gemini-api-key") or \
   not os.path.isfile("claud-api-key") or \
   not os.path.isfile("openai-api-key") or \
   not os.path.isfile("grok-api-key") or \
   not os.path.isfile("llama-api-key") or \
   not os.path.isfile("hugface-api-key"):
  print("please add api keys")
  exit(-1)

from gemini import Gemini, Gemini2
from claud import  Claud
from openai import Openai, Openai2
from grok import Grok, Grok2
from llama import Llama, Llama2
from hugface import HugFace, HugFace2, HugFace3
from faulty import Faulty

# The models and order of responses (skiping any not in schedule). Need at least 3 different models for 3 way comparisons.
# Order by preference for answers.
models = [Gemini, Gemini2, Claud, Openai, Openai2, Grok, Grok2, Llama, Llama2, HugFace, HugFace2, HugFace3, Faulty]

# The models that can be used for comparisons (skipping any not in comparison schedule). 
# Order by prefence for comparisons. Need at least 3 models for 3-way comparisons. 
# Can add a model more than once but that can't be configured via the Web UI.
comparison_models = [Openai, Gemini, Claud, Grok2, Llama, Faulty]

# use another model for comparison than those used for queries if true
# use models from the comparion list in order if false.
diff_comparator = True 

def get_diff_comparator():
  return diff_comparator

def set_diff_comparator(value):
  global diff_comparator
  diff_comparator = value

max_no_models = 5

T = True
F = False

# Which models to query
schedule = {
  "gemini": T,
  "gemini2": F,
  "openai": T,
  "openai2": F,
  "claud": T,
  "grok": F,
  "grok2": F,
  "llama": F,
  "llama2": F,
  "hugface": F,
  "hugface2": F,
  "hugface3": F,
  "faulty": F
}

# Which models to use for comparisons
comparison_schedule = {
  "gemini": T,
  "openai": T,
  "claud": T,
  "grok2": F,
  "llama": F,
  "hugface": F,
  "faulty": F
}

# model versions to use for queries
model_versions = {
  "gemini": "gemini-1.5-flash-latest",
  "gemini2": "gemini-2.0-flash-exp",
  "claud": "claude-3-5-sonnet-20241022",
  "openai": "gpt-4o",
  "openai2": "chatgpt-4o-latest",
  "grok": "grok-beta",
  "grok2": "grok-2-latest",
  "llama": "llama3-8b",
  "llama2": "llama3.3-70b",
  "hugface": "google/gemma-2-2b-it",
  "hugface2": "microsoft/Phi-3-mini-4k-instruct",
  "hugface3": "Qwen/Qwen2.5-7B-Instruct"
}


web_comparisons = ["1-way", "3-way", "n-way", "none" ]
default_web_comparison = web_comparisons.index("3-way")

def configure():
  # Push down the model configuration to imported models to reflect any changes above.
  Gemini.model = model_versions["gemini"]
  Gemini2.model = model_versions["gemini2"]
  Claud.model = model_versions["claud"]
  Openai.model = model_versions["openai"]
  Openai2.model = model_versions["openai2"]
  Grok.model = model_versions["grok"]
  Grok2.model = model_versions["grok2"]
  Llama.model = model_versions["llama"]
  Llama2.model = model_versions["llama2"]
  HugFace.model = model_versions["hugface"]
  HugFace2.model = model_versions["hugface2"]
  HugFace3.model = model_versions["hugface3"]

client_timeout_seconds = 30

debug = False
trail_only = True

def display(trail, text):
  if not trail_only: print(text)
  trail.append(text)

def set_trail_only(b):
  global trail_only
  trail_only = b