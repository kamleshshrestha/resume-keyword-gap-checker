# Resume Gap Checker

A small web tool that compares a resume against a job description and returns a match score, matched keywords, and missing keywords — using the Gemini API directly, no LLM framework in between.

Built as Project 1 of a 10-project series learning LLM development from raw API calls up to multi-agent, self-auditing systems.

## What it does

1. Paste a job description and a resume into the browser
2. The Flask backend sends both to the Gemini API with a prompt that forces structured JSON output
3. The UI shows a 0–100 match score, a one-line verdict, and two lists: keywords you have, keywords you're missing

## Why this exists (learning goals)

This project is deliberately built the "hard way" — no SDK abstractions, no JSON-mode/schema enforcement, no framework. The goal is to understand what's actually happening under the hood before relying on tooling that hides it:

- Calling an LLM API with raw HTTP and understanding the request/response shape
- Controlling output determinism via `temperature`
- Getting structured data out of a model using prompting alone, plus defensive parsing for when it doesn't comply
- Understanding why the API key must live server-side, never in browser JS

## Stack

- **Backend:** Python, Flask
- **LLM:** Gemini API (raw REST calls, no SDK)
- **Frontend:** Single HTML file, vanilla JS, no build step

## Setup

### 1. Clone and install dependencies

```bash
git clone <your-repo-url>
cd resume-gap-checker
pip install -r requirements.txt
```

### 2. Get a Gemini API key

Get one from [Google AI Studio](https://aistudio.google.com/apikey). Free tier is enough for testing this.

### 3. Set your API key as an environment variable

```bash
export GEMINI_API_KEY="your-key-here"
```

Never commit your key or hardcode it in `app.py`. This repo's `.gitignore` should exclude any `.env` file if you add one.

### 4. Run it

```bash
python app.py
```

Open `http://localhost:5000` in your browser.

## Project structure

```
resume-gap-checker/
├── app.py                 # Flask backend + Gemini API calls
├── templates/
│   └── index.html         # Single-page UI
├── requirements.txt
└── README.md
```

## How it works

- `build_prompt()` constructs a prompt instructing the model to return only JSON in a fixed shape (`match_score`, `missing_keywords`, `matched_keywords`, `one_line_verdict`)
- `call_gemini()` sends that prompt to the Gemini API via raw `requests`, with `temperature` set low (~0.1) to keep scoring consistent across repeated runs on the same input
- `parse_model_json()` defensively strips markdown fences and parses the response, since prompting-based JSON isn't guaranteed the way schema/tool-calling APIs are
- The Flask route `/analyze` receives form data from the browser, calls Gemini, and returns JSON to the frontend, which renders it

## Known limitations

- No persistence — results aren't saved between sessions
- JSON parsing can fail if the model adds commentary despite instructions; failures are surfaced in the UI rather than crashing
- No auth, no rate limiting — not meant for public deployment as-is

## What's next

This is Project 1 in a series. Project 2 moves to few-shot prompting and output consistency testing; Project 3 replaces manual JSON parsing with actual structured-output/function-calling. See [series repo/index if applicable].

## License

MIT (or your choice)
