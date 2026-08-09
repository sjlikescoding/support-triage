# test_main.py
#
# Phase C goal: get a test runner working, testing only the deterministic
# parts of our code.
#
# Phase D goal: add a test for classify() using a MOCK - a fake stand-in for
# the real API call. This lets us test our JSON-parsing/fallback logic
# without hitting the real network, without spending money, and without
# the test being "flaky" (real APIs can occasionally be slow or return
# slightly different wording even for the same input).

from unittest.mock import patch, MagicMock
from main import tickets, respond, classify


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


# --- Step D2: classify() tests using a mock ---
#
# @patch("main.client") replaces the real `client` object inside main.py
# with a fake one, ONLY for the duration of this test function. The fake
# object gets passed in as the `mock_client` argument automatically.
#
# We then tell the fake client exactly what to return when
# generate_content(...) is called, so we can test how classify() PARSES
# that response, without ever making a real network call.

@patch("main.client")
def test_classify_parses_valid_json_response(mock_client):
    # Set up the fake response the mock client will "return" when called.
    fake_response = MagicMock()
    fake_response.text = '{"category": "billing", "urgency": "high"}'
    mock_client.models.generate_content.return_value = fake_response

    result = classify("I was charged twice!")

    assert result == {"category": "billing", "urgency": "high"}


@patch("main.client")
def test_classify_falls_back_on_garbage_response(mock_client):
    # Simulate the model misbehaving and returning something that isn't
    # valid JSON at all. classify() should fall back to safe defaults
    # instead of crashing.
    fake_response = MagicMock()
    fake_response.text = "sorry, I cannot help with that"
    mock_client.models.generate_content.return_value = fake_response

    result = classify("some ticket")

    assert result == {"category": "general", "urgency": "medium"}


@patch("main.client")
def test_classify_strips_markdown_code_fences(mock_client):
    # Simulate the model wrapping its JSON in a markdown code fence,
    # which we know happens sometimes even when we ask it not to.
    fake_response = MagicMock()
    fake_response.text = '```json\n{"category": "shipping", "urgency": "low"}\n```'
    mock_client.models.generate_content.return_value = fake_response

    result = classify("where is my order")

    assert result == {"category": "shipping", "urgency": "low"}

