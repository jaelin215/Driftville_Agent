import time

from dotenv import load_dotenv
from ollama import Client

use_stream = False
load_dotenv()
start_time = time.time()

client = Client()
messages = [
    {
        "role": "user",
        "content": "what is DMN neuroscience?",
    },
]

if use_stream:
    for part in client.chat("gpt-oss:120b-cloud", messages=messages, stream=use_stream):
        print(part["message"]["content"], end="", flush=True)
else:
    response = client.chat("gpt-oss:120b-cloud", messages=messages, stream=use_stream)
    print(response["message"]["content"])

end_time = time.time()
elapsed_time = end_time - start_time
print(f"\nResponse time: {elapsed_time:.2f} seconds")
