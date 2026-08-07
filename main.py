# main.py
#
# Phase A goal: prove that data can flow end-to-end through the pipeline.
# Nothing here is "smart" yet - classify() and respond() are stubs.
# That's intentional. We're proving the plumbing works before adding intelligence.

# --- Step A1: our fake "incoming tickets" ---
# In real life these would come from an inbox or a database.
# For now, just a plain Python list of strings.
tickets = [
    "My order hasn't arrived and it's been two weeks.",
    "I was charged twice for my last subscription payment.",
    "How do I reset my password?",
]


# --- Step A2: classify() stub ---
# Takes a ticket (a string) and returns a category.
# For now it ALWAYS returns "general", no matter what the ticket says.
# We'll make this real in Phase B.
def classify(ticket):
    return "general"


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
