from gemini import Gemini, Gemini2
from claud import  Claud
from openai import Openai, Openai2
from grok import Grok
from llama import Llama, Llama2
from hugface import HugFace, HugFace2, HugFace3

# The models and order of responses (skiping any not in schedule). Need at least 3 different models for 3 way comparisons.
# Order by preference for answers.
models = [Gemini, Gemini2, Claud, Openai, Openai2, Grok, Llama, Llama2, HugFace, HugFace2, HugFace3]

# The models to use for comparisons. Order by prefence for comparisons.
# Need at least 3 models for 3-way. They can be the same model applied more than once.
comparison_models = [Openai, Gemini, Claud, Grok, Llama] 

# use another model for comparison than those used for queries if true
# use models from the comparion list in order if false.
diff_comparator = True 

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
  "grok": T,
  "llama": T,
  "llama2": F,
  "hugface": F,
  "hugface2": F,
  "hugface3": F
}

# model versions to use for queries
model_versions = {
  "gemini": "gemini-1.5-flash-latest",
  "gemini2": "gemini-2.0-flash-exp",
  "claud": "claude-3-5-sonnet-20241022",
  "openai": "gpt-4o",
  "openai2": "chatgpt-4o-latest",
  "grok": "grok-beta",
  "llama": "llama3.2-3b",
  "llama2": "llama3.3-70b",
  "hugface": "google/gemma-2-2b-it",
  "hugface2": "microsoft/Phi-3-mini-4k-instruct",
  "hugface3": "Qwen/Qwen2.5-7B-Instruct"
}

web_comparisons = ["1-way", "3-way", "n-way" ]

def configure():
  # Push down the model configuration to imported models to reflect any changes above.
  Gemini.model = model_versions["gemini"]
  Gemini2.model = model_versions["gemini2"]
  Claud.model = model_versions["claud"]
  Openai.model = model_versions["openai"]
  Openai2.model = model_versions["openai2"]
  Grok.model = model_versions["grok"]
  Llama.model = model_versions["llama"]
  Llama2.model = model_versions["llama2"]
  HugFace.model = model_versions["hugface"]
  HugFace2.model = model_versions["hugface2"]
  HugFace3.model = model_versions["hugface3"]
