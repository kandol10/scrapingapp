from flask import Flask, request, jsonify
from RestrictedPython import compile_restricted_exec

app = Flask(__name__)

def safe_execute(code, context):
    """Executes the provided Python code safely in a restricted environment."""
    try:
        byte_code = compile_restricted_exec(code)
        exec(byte_code, {"__builtins__": {}}, context)
    except Exception as e:
        return {"error": str(e)}

    return context

@app.route('/evaluate_code', methods=['POST'])
def evaluate_code():
    user_code = request.json['code']
    expected_output = request.json['expected_output']
    
    # Context where the output should be stored by the user code
    context = {"output": None}
    result = safe_execute(user_code, context)
    
    if 'error' in result:
        return jsonify(result), 400

    # Check if the user's output matches the expected output
    if context['output'] == expected_output:
        return jsonify({"result": "Correct"})
    else:
        return jsonify({"result": "Incorrect", "expected": expected_output, "received": context['output']})

if __name__ == '__main__':
    app.run(debug=True)
