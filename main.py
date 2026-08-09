# main.py
#
# Phase D goal: classify() now also returns urgency, alongside category.
# We ask the model for both in a single call (not two separate calls) and
# get the result back as structured JSON. Everything else (routing,
# drafting, review) stays exactly as trivial as before.

import os
import json
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

# The only categories and urgency levels we want back.
CATEGORIES = ["billing", "technical", "shipping", "general"]
URGENCY_LEVELS = ["high", "medium", "low"]

# --- Step A1: our fake "incoming tickets" ---
# In real life these would come from an inbox or a database.
# For now, just a plain Python list of strings.
tickets = [
    "My order hasn't arrived and it's been two weeks.",
    "I was charged twice for my last subscription payment.",
    "How do I reset my password?",
]


# --- Step D1: classify() now returns BOTH category and urgency ---
# Takes a ticket (a string), asks Gemini for both fields in one call,
# and returns them as a dict, e.g. {"category": "billing", "urgency": "high"}.
#
# Why a dict instead of two separate return values or two functions?
# A dict is easy to extend later (e.g. adding a "confidence" field) without
# changing every place that calls classify().
def classify(ticket):
    prompt = (
        "You are classifying a customer support ticket.\n\n"
        f"Ticket: \"{ticket}\"\n\n"
        f"Pick exactly one category from: {', '.join(CATEGORIES)}.\n"
        f"Pick exactly one urgency level from: {', '.join(URGENCY_LEVELS)}.\n\n"
        "Reply with ONLY valid JSON, nothing else, in exactly this shape:\n"
        '{"category": "...", "urgency": "..."}'
    )

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
    )

    # The model should reply with pure JSON, but models sometimes wrap
    # output in markdown code fences (```json ... ```) even when told not
    # to. Strip those defensively before parsing.
    raw_text = response.text.strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    try:
        parsed = json.loads(raw_text)
        category = str(parsed.get("category", "")).strip().lower()
        urgency = str(parsed.get("urgency", "")).strip().lower()
    except (json.JSONDecodeError, AttributeError):
        # If the model returned something we couldn't parse at all,
        # fall back to safe defaults rather than crashing the pipeline.
        category = ""
        urgency = ""

    if category not in CATEGORIES:
        category = "general"
    if urgency not in URGENCY_LEVELS:
        urgency = "medium"

    return {"category": category, "urgency": urgency}


# --- Step A3: respond() stub ---
# Takes a ticket and its category, returns a canned response string.
# Also intentionally dumb for now - same response every time.
def respond(ticket, category):
    return "Thanks for reaching out. A member of our team will follow up shortly."


# --- Step D3: wire it together ---
# Loop over every ticket, run it through classify() and respond(),
# and print what happened, now including urgency.
def main():
    for i, ticket in enumerate(tickets, start=1):
        result = classify(ticket)
        category = result["category"]
        urgency = result["urgency"]
        response = respond(ticket, category)

        print(f"--- Ticket {i} ---")
        print(f"Text:     {ticket}")
        print(f"Category: {category}")
        print(f"Urgency:  {urgency}")
        print(f"Response: {response}")
        print()


# This is a Python convention: only run main() if this file is executed
# directly (e.g. `python main.py`), not if it's imported elsewhere later.
if __name__ == "__main__":
    main()

