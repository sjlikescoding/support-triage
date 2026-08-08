# test_main.py
#
# Phase C goal: get a test runner working, testing only the deterministic
# parts of our code. We deliberately do NOT test classify() here - it calls
# a real API, which would make tests slow, flaky, and cost money on every run.
# We'll handle testing AI-calling code properly with mocking in Phase D.

from main import tickets, respond


def test_tickets_list_has_three_entries():
    # A simple sanity check: our fake ticket data hasn't accidentally
    # been changed to have more or fewer entries than we expect.
    assert len(tickets) == 3


def test_respond_returns_canned_string():
    # respond() is still a stub - it should always return the exact
    # same string, no matter what ticket or category is passed in.
    result = respond("any ticket text", "any category")
    assert result == "Thanks for reaching out. A member of our team will follow up shortly."


def test_respond_ignores_its_inputs():
    # Since respond() is a stub, calling it with wildly different inputs
    # should still give the same output. This test exists mainly to make
    # it obvious later (in Phase G) when respond() stops being a stub -
    # this test will start failing, which is a deliberate tripwire.
    result_a = respond("ticket A", "billing")
    result_b = respond("completely different ticket", "shipping")
    assert result_a == result_b
