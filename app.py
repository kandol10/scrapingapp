from flask import Flask, request, jsonify

app = Flask(__name__)

# Define the questions and test cases
questions = {
    1: {
        "name": "Binary to Decimal",
        "prompt": "Write a function bin_to_dec that converts a binary string to a decimal integer.",
        "test_cases": [
            {"input": "bin_to_dec('101')", "expected_output": 5},
            {"input": "bin_to_dec('111')", "expected_output": 7},
            {"input": "bin_to_dec('100')", "expected_output": 4}
        ]
    },
    2: {
        "name": "Sum of Two Numbers",
        "prompt": "Write a function sum_two_numbers that returns the sum of two numbers.",
        "test_cases": [
            {"input": "sum_two_numbers(2, 3)", "expected_output": 5},
            {"input": "sum_two_numbers(10, 5)", "expected_output": 15},
            {"input": "sum_two_numbers(0, 0)", "expected_output": 0}
        ]
    }
}

def safe_execute(user_code, question_id):
    """Executes the provided Python code safely and evaluates against test cases."""
    context = {}
    feedback = []
    score = 0
    total_tests = len(questions[question_id]["test_cases"])
    
    try:
        compiled_code = compile(user_code, '<string>', 'exec')
        exec(compiled_code, context)
    except Exception as e:
        return {"error": str(e), "feedback": "Code compilation or execution failed"}

    for test_case in questions[question_id]["test_cases"]:
        input_expression = test_case['input']
        expected_output = test_case['expected_output']
        try:
            output = eval(input_expression, context)
            if output == expected_output:
                score += 1
                feedback.append({"input": input_expression, "result": "Correct", "received": output})
            else:
                feedback.append({"input": input_expression, "result": "Incorrect", "expected": expected_output, "received": output})
        except Exception as e:
            feedback.append({"input": input_expression, "result": "Error", "error": str(e)})

    return {"score": score, "total_tests": total_tests, "feedback": feedback}

@app.route('/evaluate_code', methods=['POST'])
def evaluate_code():
    try:
        data = request.get_json()
        user_code = data['code']
        question_id = data['question_id']
        
        print(f"Received code: {user_code}")  # Debugging output

        # Check if the code and question ID are provided
        if not user_code or not question_id:
            raise ValueError("Missing 'code' or 'question_id' in the JSON data")

        # Execute the code safely
        result = safe_execute(user_code, question_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
