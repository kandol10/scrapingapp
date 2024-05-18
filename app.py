from flask import Flask, request, jsonify
from RestrictedPython import compile_restricted_exec

app = Flask(__name__)

def safe_execute(code, context):
    """Executes the provided Python code safely in a restricted environment."""
    try:
        # Check if the code is a string and log its type
        if not isinstance(code, str):
            raise ValueError("Code is not a string")
        print(f"Code to execute: {code}")
        
        compile_result = compile_restricted_exec(code, '<string>', 'exec')
        byte_code = compile_result.code  # Extract the code object
        print(f"Compiled byte code: {byte_code}")
        
        # Additional debug statement
        print(f"Type of byte_code: {type(byte_code)}")
        
        exec(byte_code, {"__builtins__": {}}, context)
    except Exception as e:
        print(f"Exception during execution: {e}")
        return {"error": str(e)}
    return context


@app.route('/evaluate_code', methods=['POST'])
def evaluate_code():
    user_code = request.json.get('code')
    expected_output = request.json.get('expected_output')

    # Log the received code to verify
    print(f"Received code: {user_code}")
    print(f"Expected output: {expected_output}")

    # Ensure the user code is a string
    if not isinstance(user_code, str):
        return jsonify({"error": "User code must be a string"}), 400

    # Context where the output should be stored by the user code
    context = {"output": None}
    result = safe_execute(user_code, context)
    
    if 'error' in result:
        return jsonify(result), 400

    # Check if the user's output matches the expected output
    if context.get('output') == expected_output:
        return jsonify({"result": "Correct"})
    else:
        return jsonify({"result": "Incorrect", "expected": expected_output, "received": context.get('output')})



if __name__ == '__main__':
    app.run(debug=True)
