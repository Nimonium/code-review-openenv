TASKS = {
    "task_easy": {
        "task_id": "task_easy",
        "code_snippet": "def add(a, b):\n    return a - b\n",
        "known_issues": ["subtraction instead of addition", "wrong operator", "logic error", "subtraction"],
        "difficulty": "easy"
    },
    "task_medium": {
        "task_id": "task_medium",
        "code_snippet": "import os\ndef read_file(filename):\n    os.system(f'cat {filename}')\n",
        "known_issues": ["command injection", "os.system", "shell injection"],
        "difficulty": "medium"
    },
    "task_hard": {
        "task_id": "task_hard",
        "code_snippet": "import pickle\nfrom flask import Flask, request\napp = Flask(__name__)\n@app.route('/load', methods=['POST'])\ndef load_data():\n    data = request.data\n    obj = pickle.loads(data)\n    return 'OK'\n",
        "known_issues": ["insecure deserialization", "pickle", "arbitrary code execution", "code execution"],
        "difficulty": "hard"
    }
}

def get_tasks():
    return TASKS