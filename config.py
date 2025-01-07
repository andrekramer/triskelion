"""configure triskelion"""
import sys
import os

# new model? import here
from gemini import Gemini, Gemini2
from claud import  Claud
from openai import Openai, Openai2
from grok import Grok, Grok2
from llama import Llama, Llama2
from hugface import HugFace, HugFace2, HugFace3
from faulty import Faulty

for file in ["gemini-api-key",
             "claud-api-key",
             "openai-api-key",
             "grok-api-key",
             "llama-api-key",
             "hugface-api-key"]:
    if not os.path.isfile(file):
        print("please add api keys")
        sys.exit(-1)

# new model? add here
# The models and order of responses (skiping any not in schedule).
# Need at least 3 different models for 3 way comparisons.
# Order by preference for answers.
models = [Gemini, Gemini2, Claud, Openai, Openai2, Grok, Grok2,
          Llama, Llama2, HugFace, HugFace2, HugFace3, Faulty]

# new model? add here if to be used for comparisons
# The models that can be used for comparisons (skipping any not in comparison schedule).
# Order by prefence for comparisons. Need at least 3 models for 3-way comparisons.
# Can add a model more than once but that can't be configured via the Web UI.
comparison_models = [Openai, Gemini, Claud, Grok2, Llama, Faulty]

T = True
F = False

# new model? add here
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

# new model? add here if to be used for comparisons
# Which models to use for comparisons
comparison_schedule = {
  "gemini": T,
  "openai": T,
  "claud": T,
  "grok2": F,
  "llama": T,
  "hugface": F,
  "faulty": F
}

# new model? add the specific model version here if you want it to be configrable
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


web_comparisons = ["1-way", "3-way", "3-twice", "n-way"]
default_web_comparison = web_comparisons.index("3-way")

# new model? add here if you want the model version to be configrable
def configure():
    """Push down the model configuration to imported models to reflect any changes above."""
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

DEBUG = False

MAX_NO_MODELS = 5

class Config:
    """Configuration Helper"""
    client_timeout_seconds = 30
    trail_only = True
    # use another model for comparison than those used for queries if true
    # use models from the comparion list in order if false.
    diff_comparator = True
    # Always use first comparison model if single simparator is true. Overrides diff comparator.
    single_comparator = False

    @classmethod
    def get_diff_comparator(cls):
        """get diff comparator config"""
        return cls.diff_comparator

    @classmethod
    def set_diff_comparator(cls, value):
        """set diff comparator config"""
        cls.diff_comparator = value

    @classmethod
    def get_single_comparator(cls):
        """get single comparator config"""
        return cls.single_comparator

    @classmethod
    def set_single_comparator(cls, value):
        """set single comparator config"""
        cls.single_comparator = value

    @classmethod
    def set_trail_only(cls, b):
        """set trail only config"""
        cls.trail_only = b

def display(trail, text):
    """display to trail and conditionally to console"""
    if not Config.trail_only:
        print(text)
    trail.append(text)
