Work in Progress   

Please see https://andrekramermsc.substack.com/p/n-versioning-ai-llm-models   

Query multiple LLMs and compare results to suppress model errors.   
The models to use and comparison action are configurable (see config.py).   
Different flavous of comparisons are possible. 3-way is probaly the sweet spot.   

Use py-install script to install dependencies.   
Create files with api keys for the models: claud-api-key, openai-api-key, llama-api-key, grok-api-key gemini-api-key  

Usage:   
python3 multi-llm.py 3-way|2-way|1-way prompt   

e.g.  
python3 multi-llm.py 3-way "Who wrote The Great Gabsby?"    
python3 multi-llm.py 1-way "What is \"The Magic Number Seven\" about?"   
python3 multi-llm.py 2-way "toss a coin"   
python3 multi-llm.py 3-all "How many number ones did the Beatles have in the UK?"   
python3 multi-llm.py n-way "What is the longest river on Mars?"
