from flask import Flask, request, jsonify
import os
from openai import OpenAI
from prompts import PROMPTS

app = Flask(__name__)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set.")
client = OpenAI(api_key=OPENAI_API_KEY)

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
    return response.choices[0].message.content.strip()

@app.route("/api/generateQuestions", methods=["POST"])
def api_generate_questions():
    # Extract the information from the request
    base_text = request.json.get("baseText") or ""
    closed_questions_amount = request.json.get("closedQuestionsAmount") or 0
    open_questions_amount = request.json.get("openQuestionsAmount") or 0

    # Generate the prompts for the API
    system_prompt = PROMPTS.QUESTION_GENERATOR_INSTRUCTION
    developer_prompt = PROMPTS.generate_questions_instruction(
        closedQuestionsAmount=closed_questions_amount,
        openQuestionsAmount=open_questions_amount
    )
    user_prompt = base_text

    # Call the API
    response = call_api(system_prompt, developer_prompt, user_prompt)

    # Return the response
    return jsonify({"quizQuestions": response})

@app.route("/api/checkOpenAnswer", methods=["POST"])
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
    example_developer_prompt = PROMPTS.generate_questions_instruction(1,1)
    example_user_prompt = (
        "This week, we will learn about functions. "
        "We will also learn about loops. "
        "Next week, we will learn about classes."
    )
    response = call_api(
        example_system_prompt,
        example_developer_prompt,
        example_user_prompt,
    )
    return jsonify({"response": response})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
