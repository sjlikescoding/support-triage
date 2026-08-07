# main.py
#
# Phase B goal: classify() now makes a real AI call. Everything else
# (respond(), routing, review) stays exactly as trivial as before.

import os
from google import genai

# Read the API key from the environment variable, same as scratch_test.py.
# Never hardcode the key directly in code.
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. Did you run the $env:GEMINI_API_KEY=... "
        "command in this terminal session?"
    )

client = genai.Client(api_key=api_key)

# The only categories we want back. We'll tell the model to pick one of these.
CATEGORIES = ["billing", "technical", "shipping", "general"]

# --- Step A1: our fake "incoming tickets" ---
# In real life these would come from an inbox or a database.
# For now, just a plain Python list of strings.
tickets = [
    "My order hasn't arrived and it's been two weeks.",
    "I was charged twice for my last subscription payment.",
    "How do I reset my password?",
]


# --- Step B5: classify() is now real ---
# Takes a ticket (a string), asks Gemini to pick one category, returns it.
def classify(ticket):
    prompt = (
        "You are classifying a customer support ticket into exactly one "
        f"category from this list: {', '.join(CATEGORIES)}.\n\n"
        f"Ticket: \"{ticket}\"\n\n"
        "Reply with ONLY the category word, nothing else."
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    # The model should reply with just the category, but let's be defensive:
    # strip whitespace and lowercase it, and fall back to "general" if it
    # returns something we don't recognize.
    category = response.text.strip().lower()

    if category not in CATEGORIES:
        category = "general"

    return category


# --- Step A3: respond() stub ---
# Takes a ticket and its category, returns a canned response string.
# Also intentionally dumb for now - same response every time.
def respond(ticket, category):
    return "Thanks for reaching out. A member of our team will follow up shortly."


# --- Step A4: wire it together ---
# Loop over every ticket, run it through classify() and respond(),
# and print what happened. This is our "does data flow end to end" check.
def main():
    for i, ticket in enumerate(tickets, start=1):
        category = classify(ticket)
        response = respond(ticket, category)

        print(f"--- Ticket {i} ---")
        print(f"Text:     {ticket}")
        print(f"Category: {category}")
        print(f"Response: {response}")
        print()


# This is a Python convention: only run main() if this file is executed
# directly (e.g. `python main.py`), not if it's imported elsewhere later.
if __name__ == "__main__":
    main()
