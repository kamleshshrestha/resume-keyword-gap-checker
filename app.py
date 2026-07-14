from flask import Flask, jsonify, request, render_template
from google import genai
import os
import re
import json
import requests
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

if "GEMINI_API_KEY" not in os.environ:
    raise RuntimeError(
        'Please set the Gemini API key before running the application.'
    )

# Build the system prompt.
def build_prompt(job_description: str, resume: str) -> str:
    """
    Build the system prompt for the Gemini API. We are using hand written prompt engineering
    instead of schema/tool calling API because we want to have more control over the output
    and we want to be able to easily change the prompt in the future.
    """
    return f"""
        You are a resume analysis engine. Compare the RESUME against the JOB DESCRIPTION below.
        Return ONLY valid JSON, no markdown fences, no commentary, no extra text. The JSON should have the EXACT following structure:
        {{
        "match_score": <integer 0-100>,
        "missing_keywords": ["keyword1", "keyword2", ...],
        "matched_keywords": ["keyword1", "keyword2", ...],
        "one_line_verdict": "<one blunt sentence>"
        }}

        JOB DESCRIPTION:
        {job_description}

        RESUME:
        {resume}
    """

def call_gemini_api(prompt: str) -> dict:
    client = genai.Client()
    interaction = client.interactions.create(
        model="gemini-3.5-flash",
        input = prompt
    )
    data = interaction.output_text
    
    if isinstance(data, list):
        raw_text = "\n".join(data).strip()
    else:
        raw_text = data.strip() if data else ""

    return parse_model_json(raw_text)

def parse_model_json(raw_text: str) -> dict:
    """
    Parse the raw text returned by the model into a JSON object.
    """
    cleaned = re.sub(r"^```(?:json)?|```$", "", raw_text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        return {
            "match_score": None,
            "missing_keywords": [],
            "matched_keywords": [],
            "one_line_verdict": f"Parse error: model did not return valid JSON. Error: {e}"
        }

@app.route('/') #This is called callable decorator, it is used to bind a function to a URL.
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    job_description = request.form.get('job_description')
    resume = request.form.get('resume')

    if not job_description or not resume:
        return jsonify({"error": "Both job description and resume are required."}), 400
    
    prompt = build_prompt(job_description, resume)
    result = call_gemini_api(prompt)
    print(result)

    # return jsonify({"result": result}) This was the mistake because now result is already a dictionary, so we can return it directly.
    return jsonify(result)

# if __name__ == '__main__':
app.run(debug=True, port=5000)