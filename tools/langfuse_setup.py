import os
from dotenv import load_dotenv

load_dotenv()

from langfuse import get_client
from openinference.instrumentation.google_adk import GoogleADKInstrumentor

langfuse = get_client()

# Verify connection
if langfuse.auth_check():
    print("Langfuse client is authenticated and ready!")
else:
    print("Authentication failed. Please check your credentials and host.")

# OpenTelemetry instrumentation
# This patches the Google ADK library globally,
# So once it's called anywherein the application,
# all subsequent ADK operations will be traced.
GoogleADKInstrumentor().instrument()
