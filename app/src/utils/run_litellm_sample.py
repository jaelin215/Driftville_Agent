###
# LiteLLM calls w/ various models
# model options: ollama/mistral:latest, gpt-3.5-turbo, openrouter/x-ai/grok-4-fast:free
###


import time

from dotenv import load_dotenv
from litellm import completion

# set callbacks
# log input/output to langfuse
# litellm.success_callback = ["langfuse"]

load_dotenv()

start_time = time.time()

#####################################
# OPTION 1: via Ollama (100% free)
#####################################
response = completion(
    model="ollama/gemma3:12b",
    messages=[
        {
            "content": "What is DMN in neuroscience?",
            "role": "user",
        }
    ],
    api_base="http://localhost:11434",
)


#####################################
# OPTION 2: via OpenRouter (some free)
#####################################
# response = completion(
#     model="gemini/gemma-3-27b-it",
#     messages=[{"content": "what is DMN inneuroscience?", "role": "user"}],
# )

#####################################
# OPTION 3: via OpenAI format (paid)
#####################################
# response = completion(
#     model="openrouter/x-ai/grok-4-fast:free",
#     messages=[{"content": "Hello, how are you?", "role": "user"}],
# )

# #####################################
# # OPTION 4: via HuggingFace (paid)
# #####################################
# response = completion(
#     model="huggingface/deepseek-ai/DeepSeek-R1-Distill-Llama-8B",
#     messages=[{"content": "Hello, how are you?", "role": "user"}],
#     api_base="https://my-endpoint.huggingface.cloud",
# )


end_time = time.time()
elapsed_time = end_time - start_time
print(f"Response time: {elapsed_time:.2f} seconds")
print(response.choices[0].message.content)
