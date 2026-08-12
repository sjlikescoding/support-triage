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
from main import tickets, classify, route, draft_response


def test_tickets_list_has_three_entries():
    # A simple sanity check: our fake ticket data hasn't accidentally
    # been changed to have more or fewer entries than we expect.
    assert len(tickets) == 3


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


# --- Step G2: draft_response() tests using a mock ---
#
# Same idea as the classify() mocked tests: replace the real API call
# with a fake one so we can test how draft_response() handles the
# response, without depending on whatever text the model happens to
# generate that day.

@patch("main.client")
def test_draft_response_returns_model_text(mock_client):
    # draft_response() shouldn't care that this text is fake, only that
    # it correctly pulls it out of the response and returns it as-is.
    fake_response = MagicMock()
    fake_response.text = "We're sorry to hear that! A refund has been issued."
    mock_client.models.generate_content.return_value = fake_response

    result = draft_response("I want a refund", "billing")

    assert result == "We're sorry to hear that! A refund has been issued."


@patch("main.client")
def test_draft_response_strips_markdown_code_fences(mock_client):
    # strip_fencing() is shared with classify() - this confirms it still
    # behaves correctly on plain (non-JSON) text, not just JSON.
    fake_response = MagicMock()
    fake_response.text = "```\nThanks, we'll look into it right away.\n```"
    mock_client.models.generate_content.return_value = fake_response

    result = draft_response("where is my package", "shipping")

    assert result == "Thanks, we'll look into it right away."

# --- Step E2: route() tests ---
#
# route() is pure logic - no API calls, no mocking needed. Just plain
# input -> expected output checks, covering each rule and how they
# interact when both could apply at once.

def test_high_urgency_routes_to_human_regardless_of_category():
    # The urgency rule should apply no matter what the category is.
    assert route("technical", "high") == "human_only"
    assert route("shipping", "high") == "human_only"
    assert route("general", "high") == "human_only"


def test_billing_routes_to_human_regardless_of_urgency():
    # The billing rule should apply even at low urgency.
    assert route("billing", "low") == "human_only"
    assert route("billing", "medium") == "human_only"


def test_billing_and_high_urgency_together_still_routes_to_human():
    # Both rules pointing the same way shouldn't cause any weirdness -
    # still just "human_only", not some special third outcome.
    assert route("billing", "high") == "human_only"


def test_non_billing_low_or_medium_urgency_routes_to_auto():
    # The "safe" cases: nothing risky about category or urgency, so
    # these should be allowed through automatically.
    assert route("technical", "low") == "auto"
    assert route("technical", "medium") == "auto"
    assert route("shipping", "low") == "auto"
    assert route("shipping", "medium") == "auto"
    assert route("general", "low") == "auto"
    assert route("general", "medium") == "auto"

