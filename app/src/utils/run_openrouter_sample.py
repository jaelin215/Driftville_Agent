import time
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

start_time = time.time()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

response = requests.post(
    url="https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    },
    data=json.dumps(
        {
            "model": "mistralai/mistral-small-3.1-24b-instruct:free",  # Optional
            "messages": [{"role": "user", "content": "What is DMN in neuroscience?"}],
        }
    ),
)


end_time = time.time()
elapsed_time = end_time - start_time
print(f"Response time: {elapsed_time:.2f} seconds")
# print(response.json()["choices"][0]["message"]["content"])
# Parse the JSON response
if response.status_code == 200:
    data = response.json()
    message_content = data["choices"][0]["message"]["content"]
    print(f"Response:\n{message_content}")
else:
    print(f"Error: {response.text}")
