import os

from dotenv import load_dotenv
from langfuse import Langfuse
from opentelemetry import trace

load_dotenv()

# Initialize Langfuse client
langfuse = Langfuse()

# Get production prompt
# prompt = langfuse.get_prompt("ORPDA/Drifter/instruction")


# Get by label
# You can use as many labels as you'd like to identify different deployment targets
prompt = langfuse.get_prompt("ORPDA/Drifter/instruction", label="latest")
# Get by version number, usually not recommended as it requires code changes to deploy new prompt versions
# prompt = langfuse.get_prompt("ORPDA/Drifter/instruction", version=1)

print(prompt.prompt)
