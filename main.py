# main.py
#
# Phase D goal: classify() now also returns urgency, alongside category.
# We ask the model for both in a single call (not two separate calls) and
# get the result back as structured JSON. Everything else (routing,
# drafting, review) stays exactly as trivial as before.

import os
import json
from google import genai
from dotenv import load_dotenv

# Load variables from a local .env file (if one exists) into the environment.
# This means GEMINI_API_KEY no longer needs to be set manually every
# terminal/debug session - it's read from .env once, automatically.
# .env is gitignored, so the real key never ends up in version control.
load_dotenv()

# Read the API key from the environment variable.
# Never hardcode the key directly in code.
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is not set. Create a .env file in this folder "
        "with a line like: GEMINI_API_KEY=your-key-here"
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

    raw_text = strip_fencing(response)

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

# The AI model should reply with pure JSON, but models sometimes wrap
# output in markdown code fences (```json ... ```) even when told not
# to. Strip those defensively before parsing.
def strip_fencing(response):
    raw_text = response.text.strip()
    raw_text = raw_text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return raw_text


# --- Step G1: draft_response() - real API call for response ---
# Will replace the calls to respond() stub with this new function.
# (Only for "auto" responses)
def draft_response(ticket, category):
    draft_prompt = (
        "Draft a response to the following customer ticket, maximum two lines.\n\n"
        f"Ticket text: {ticket}\n"
        f"Category: {category}\n"
        )

    drafted_response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=draft_prompt,
    )

    response_text = strip_fencing(drafted_response)

    return response_text


# --- Step E1: route() - our first real decision point ---
# Pure function: no API calls, no side effects, just logic. Given a
# category and urgency, decide whether this ticket is safe to auto-handle
# or needs a human to look at it first.
#
# Rule (deliberately conservative for a first version):
#   - High urgency ALWAYS goes to a human, regardless of category.
#   - Billing ALWAYS goes to a human, regardless of urgency, since money
#     mistakes are costlier to get wrong than most other categories.
#   - Everything else goes to auto.
def route(category, urgency):
    if urgency == "high":
        return "human_only"
    if category == "billing":
        return "human_only"
    return "auto"


# --- Step E3: wire it together ---
# Loop over every ticket, classify it, decide routing, and (for now) just
# log what WOULD happen next. Drafting doesn't exist yet - that's Phase G.
def main():
    for i, ticket in enumerate(tickets, start=1):
        result = classify(ticket)
        category = result["category"]
        urgency = result["urgency"]
        decision = route(category, urgency)

        print(f"--- Ticket {i} ---")
        print(f"Text:     {ticket}")
        print(f"Category: {category}")
        print(f"Urgency:  {urgency}")
        print(f"Routing:  {decision}")

        if decision == "auto":
            response = draft_response(ticket, category)
            print(f"Response: {response}")
        else:
            print("Response: (sent to human review queue - no draft yet)")

        print()


# This is a Python convention: only run main() if this file is executed
# directly (e.g. `python main.py`), not if it's imported elsewhere later.
if __name__ == "__main__":
    main()

