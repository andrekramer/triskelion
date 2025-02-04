"""configure triskelion"""
import sys
import os

# new model? import here
from gemini import Gemini, Gemini2
from claud import  Claud
from openai import Openai, Openai2, Openai3
from grok import Grok, Grok2
from llama import Llama, Llama2
from hugface import HugFace, HugFace2, HugFace3
from deepseek import Deepseek, Deepseek2
from localhost import LocalHost
from faulty import Faulty

for file in ["gemini-api-key",
             "claud-api-key",
             "openai-api-key",
             "grok-api-key",
             "llama-api-key",
             "hugface-api-key",
             "deepseek-api-key"]:
    if not os.path.isfile(file):
        print("please add api keys file " + file)
        sys.exit(-1)

# new model? add here
# The models and order of responses (skiping any not in schedule).
# Need at least 3 different models for 3 way comparisons.
# Order by preference for answers.
models = [Gemini, Gemini2, Claud, Openai, Openai2, Openai3, Grok, Grok2,
          Llama, Llama2, HugFace, HugFace2, HugFace3, Deepseek, Deepseek2,
          LocalHost, Faulty]

# new model? add here if to be used for comparisons
# The models that can be used for comparisons (skipping any not in comparison schedule).
# Order by prefence for comparisons. Need at least 3 models for 3-way comparisons.
# Can add a model more than once but that can't be configured via the Web UI.
comparison_models = [Openai, Openai2, Gemini, Claud, Grok2,
                     Llama, Deepseek, Deepseek2,
                     LocalHost, Faulty]

TestModel = Openai2 #  LocalHost, or say Openai3 (o3-mini currently needs high tier API key)

T = True
F = False

# new model? add here
# Which models to query
schedule = {
  "gemini": T,
  "gemini2": F,
  "openai": T,
  "openai2": F,
  "openai3": F,
  "claud": T,
  "grok": F,
  "grok2": F,
  "llama": F,
  "llama2": F,
  "hugface": F,
  "hugface2": F,
  "hugface3": F,
  "deepseek": F,
  "deepseek2": F,
  "localhost": F,
  "faulty": F
}

# new model? add here if to be used for comparisons
# Which models to use for comparisons
comparison_schedule = {
  "gemini": T,
  "openai": T,
  "openai2": F,
  "claud": T,
  "grok2": F,
  "llama": T,
  "hugface": F,
  "deepseek": F,
  "deepseek2": F,
  "localhost": F,
  "faulty": F
}

# new model? add the specific model version here if you want it to be configrable
# model versions to use for queries
model_versions = {
  "gemini": "gemini-1.5-flash-latest",
  "gemini2": "gemini-2.0-flash-exp",
  "claud": "claude-3-5-sonnet-20241022",
  "openai": "gpt-4o",
  "openai2": "o1-mini",
  "openai3": "o3-mini",
  "grok": "grok-beta",
  "grok2": "grok-2-latest",
  "llama": "llama3.3-70b",
  "llama2": "llama3-8b",
  "hugface": "google/gemma-2-2b-it",
  "hugface2": "microsoft/Phi-3-mini-4k-instruct",
  "hugface3": "Qwen/Qwen2.5-7B-Instruct",
  "deepseek": "deepseek-chat",
  "deepseek2": "deepseek-reasoner",
}


web_comparisons = ["1-way", "3-way", "3-twice", "n-way"]
default_web_comparison = web_comparisons.index("3-way")

web_critiques = ["critique", "summarize", "rank", "combine"]
default_web_critique = web_critiques.index("critique")

web_tests = ["test" ]
default_web_test = web_tests.index("test")

actors = ["Alice", "Bob", "Eve", "Jane", "John", "Mary", "Sam", "Sue", "Tom", "Zoe"]

# new model? add here if you want the model version to be configrable
def configure():
    """Push down the model configuration to imported models to reflect any changes above."""
    Gemini.model = model_versions["gemini"]
    Gemini2.model = model_versions["gemini2"]
    Claud.model = model_versions["claud"]
    Openai.model = model_versions["openai"]
    Openai2.model = model_versions["openai2"]
    Openai3.model = model_versions["openai3"]
    Grok.model = model_versions["grok"]
    Grok2.model = model_versions["grok2"]
    Llama.model = model_versions["llama"]
    Llama2.model = model_versions["llama2"]
    HugFace.model = model_versions["hugface"]
    HugFace2.model = model_versions["hugface2"]
    HugFace3.model = model_versions["hugface3"]
    Deepseek.model = model_versions["deepseek"]
    Deepseek2.model = model_versions["deepseek2"]

DEBUG = False

MAX_NO_MODELS = 5

DEFAULT_NO_MODELS = 3

class Config:
    """Configuration Helper"""
    # timeout on model querries in seconds - set high for thinking models
    client_timeout_seconds = 60 * 2
    # only write to the trail if true else also write to console
    trail_only = True
    # use another model for comparison than those used for queries if true
    # use models from the comparion list in order if false.
    diff_comparator = True
    # Always use first comparison model if single simparator is true. Overrides diff comparator.
    single_comparator = False
    # Justify comparisons with explanations if true
    justify = False
    # include query in comparison prompts in an answer style comparison
    # or make a statement style comparison (without including the original query) if false
    include_query = True

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

    @classmethod
    def set_justify(cls, value):
        """set justify config"""
        cls.justify = value

    @classmethod
    def get_justify(cls):
        """get justify config"""
        return cls.justify

    @classmethod
    def get_include_query(cls):
        """get include query config"""
        return cls.include_query

    @classmethod
    def set_include_query(cls, value):
        """set include query config"""
        cls.include_query = value

def display(trail, text):
    """display to trail and conditionally to console"""
    if not Config.trail_only:
        print(text)
    trail.append(text)
