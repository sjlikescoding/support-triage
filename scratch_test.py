# scratch_test.py
#
# Throwaway script - just confirms our API key + SDK setup works.
# Not part of the real pipeline. Delete or ignore this after it passes.

import os
from google import genai

# Read the key from the environment variable we set in the terminal.
# Never hardcode the key directly in code.
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. Did you run the $env:GEMINI_API_KEY=... "
        "command in this terminal session?"
    )

client = genai.Client(api_key=api_key)

response = client.models.generate_content(
    model="gemini-3.5-flash-lite",
    contents="Reply with exactly one word: hello",
)

print("Raw response text:", response.text)

# Testing new ssh remote with a comment line.
