# Support Triage (learning project)

A small AI-assisted customer support triage pipeline, built incrementally
to practice managing AI-integration work as an engineering manager.

Currently implements:
- Fake ticket ingestion (hardcoded list)
- AI-based classification (Gemini API) into billing / technical / shipping / general
- Stubbed response generation (not yet AI-generated)

## Setup

1. Install dependencies:
   ```
   pip install google-genai pytest
   ```
2. Set your Gemini API key as an environment variable:
   ```
   $env:GEMINI_API_KEY="your-key-here"
   ```
   (Get a key at https://aistudio.google.com)

## Run

```
python main.py
```

## Test

```
python -m pytest test_main.py -v
```

## Project status

Built iteratively, one small piece at a time. See commit history for
the sequence of changes.
