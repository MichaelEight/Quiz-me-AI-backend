from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from prompts import PROMPTS
from decorators import not_implemented_yet
import os
import json
import logging

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
client = OpenAI(api_key=OPENAI_API_KEY)

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def call_api(system_prompt, developer_prompt, user_prompt):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "developer", "content": developer_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    # ✅ Extract the content from OpenAI response
    response_text = response.choices[0].message.content.strip()

    # ✅ Convert the text response into a valid JSON object
    try:
        response_json = json.loads(response_text)
        return response_json  # This will return a Python dictionary (not a string)
    except json.JSONDecodeError:
        print("❌ Failed to parse OpenAI response as JSON. Returning raw text.")
        return {"error": "Invalid response format", "raw_response": response_text}

@app.route("/api/generateQuestions", methods=["POST"])
def api_generate_questions():
    # Extract the information from the request
    base_text = request.json.get("baseText") or ""
    closed_questions_amount = request.json.get("closedQuestionsAmount") or 0
    open_questions_amount = request.json.get("openQuestionsAmount") or 0

    app.logger.info(f"Received baseText={base_text!r}")
    app.logger.info(f"Received closedQuestionsAmount={closed_questions_amount!r}")
    app.logger.info(f"Received openQuestionsAmount={open_questions_amount!r}")

    # Generate the prompts for the API
    system_prompt = PROMPTS.QUESTION_GENERATOR_INSTRUCTION
    developer_prompt = PROMPTS.generate_questions_instruction(
        closedQuestionsAmount=closed_questions_amount,
        openQuestionsAmount=open_questions_amount
    )
    user_prompt = base_text

    # Call the API
    response_json = call_api(system_prompt, developer_prompt, user_prompt)

    app.logger.info(f"Generated reponse={response_json!r}")

    # Return the response
    return jsonify(response_json)

# TODO: Implement
@app.route("/api/checkOpenAnswer", methods=["POST"])
@not_implemented_yet
def api_check_open_answer():
    open_question = request.json.get("openQuestion") or ""
    answer = request.json.get("answer") or ""

    # Call the API to check if the answer is considered correct

    # if answer.lower() in open_question.lower():
    #     return jsonify({"acceptable": True})
    return jsonify({"acceptable": False})

@app.route("/api/testGPTAPI", methods=["GET"])
def api_test_gpt():
    example_system_prompt = PROMPTS.QUESTION_GENERATOR_INSTRUCTION
    example_developer_prompt = PROMPTS.generate_questions_instruction(
        closedQuestionsAmount=1,
        openQuestionsAmount=1
    )
    example_user_prompt = (
        "This week, we will learn about functions. "
        "We will also learn about loops. "
        "Next week, we will learn about classes."
    )

    response_json = call_api(
        example_system_prompt,
        example_developer_prompt,
        example_user_prompt,
    )

    return jsonify(response_json)

@app.route("/api/testAPIConnection", methods=["GET"])
def api_test_connection():
    return jsonify("OK")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
