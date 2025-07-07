from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
import os
import subprocess
import tempfile
import threading
import time

class CodeAssistant:
    def __init__(self):
        self.conversation_history = []
        self.code_snippets = {
            "Python": {
                "Function": "def function_name(param1, param2):\n    '''Description'''\n    return result",
                "Class": "class ClassName:\n    def __init__(self, param):\n        self.param = param\n    \n    def method(self):\n        pass",
                "Try-Except": "try:\n    # Code here\n    pass\nexcept Exception as e:\n    print(f'Error: {e}')",
                "File Reading": "with open('filename.txt', 'r') as file:\n    content = file.read()",
                "API Request": "import requests\nresponse = requests.get('https://api.example.com/data')\ndata = response.json()"
            },
            "JavaScript": {
                "Function": "function functionName(param1, param2) {\n    return result;\n}",
                "Arrow Function": "const functionName = (param1, param2) => {\n    return result;\n};",
                "Class": "class ClassName {\n    constructor(param) {\n        this.param = param;\n    }\n    \n    method() {\n        return this.param;\n    }\n}",
                "Async Function": "async function fetchData() {\n    try {\n        const response = await fetch('url');\n        const data = await response.json();\n        return data;\n    } catch (error) {\n        console.error('Error:', error);\n    }\n}"
            }
        }
        
    def generate_response(self, message, current_code=""):
        message_lower = message.lower()
        
        if "help" in message_lower:
            return self.get_help_response(message_lower, current_code)
        elif "explain" in message_lower:
            return self.explain_code(current_code)
        elif "debug" in message_lower or "fix" in message_lower:
            return self.debug_code(current_code)
        elif "write" in message_lower or "create" in message_lower:
            return self.suggest_code(message)
        elif "optimize" in message_lower:
            return self.optimize_code(current_code)
        else:
            return self.general_response(message)
    
    def get_help_response(self, message, code):
        if "function" in message:
            return """Here's how to write good functions:

1. **Single Responsibility**: Each function should do one thing well
2. **Clear Naming**: Use descriptive names
3. **Documentation**: Add docstrings

Example:
```python
def calculate_area(length: float, width: float) -> float:
    '''Calculate rectangle area'''
    return length * width
```"""
        elif "debug" in message:
            return self.debug_code(code)
        else:
            return """I can help with:
• Writing code examples
• Explaining programming concepts  
• Debugging errors
• Code optimization
• Best practices

Try asking: 'write a function to sort a list' or 'explain this code'"""

    def explain_code(self, code):
        if not code.strip():
            return "Please paste code in the editor for me to explain!"
        
        lines = code.strip().split('\n')
        functions = [line for line in lines if line.strip().startswith('def ')]
        classes = [line for line in lines if line.strip().startswith('class ')]
        
        response = f"**Code Analysis:**\n\n"
        response += f"• {len(lines)} lines of code\n"
        response += f"• {len(functions)} functions\n"
        response += f"• {len(classes)} classes\n\n"
        
        if functions:
            response += "**Functions found:**\n"
            for func in functions[:3]:
                response += f"• {func.strip()}\n"
                
        if classes:
            response += "\n**Classes found:**\n"
            for cls in classes[:3]:
                response += f"• {cls.strip()}\n"
                
        return response

    def debug_code(self, code):
        if not code.strip():
            return "Please paste your code so I can help debug it!"
            
        issues = []
        
        if "=" in code and "==" not in code and "print" in code:
            issues.append("• Check if you meant to use == for comparison")
            
        if code.count("(") != code.count(")"):
            issues.append("• Unmatched parentheses")
            
        if code.count("[") != code.count("]"):
            issues.append("• Unmatched brackets")
            
        response = "**Debugging Tips:**\n\n"
        
        if issues:
            response += "**Potential Issues:**\n"
            for issue in issues:
                response += f"{issue}\n"
            response += "\n"
            
        response += """**General Debug Steps:**
1. Add print statements to track values
2. Check variable types with type()
3. Use try-except blocks
4. Verify function inputs/outputs
5. Test with simple inputs first"""
        
        return response

    def optimize_code(self, code):
        if not code.strip():
            return "Please paste code for optimization suggestions!"
            
        suggestions = []
        
        if "for" in code and "append" in code:
            suggestions.append("• Consider list comprehensions instead of loops with append")
            
        if code.count("for") > 2:
            suggestions.append("• Multiple nested loops - consider algorithmic improvements")
            
        response = "**Optimization Suggestions:**\n\n"
        
        if suggestions:
            for suggestion in suggestions:
                response += f"{suggestion}\n"
            response += "\n"
            
        response += """**General Tips:**
1. Use built-in functions (they're faster)
2. Avoid premature optimization
3. Profile your code first
4. Consider time/space complexity
5. Cache repeated calculations"""
        
        return response

    def suggest_code(self, message):
        if "sort" in message.lower():
            return """**Sorting in Python:**

```python
# Sort list in place
numbers = [3, 1, 4, 1, 5]
numbers.sort()

# Return new sorted list
sorted_numbers = sorted(numbers)

# Custom sorting
students = [('Alice', 85), ('Bob', 75)]
students.sort(key=lambda x: x[1])  # Sort by grade
```"""
        elif "file" in message.lower():
            return """**File Operations:**

```python
# Reading
with open('file.txt', 'r') as f:
    content = f.read()

# Writing
with open('output.txt', 'w') as f:
    f.write('Hello World')

# Appending
with open('log.txt', 'a') as f:
    f.write('New entry\\n')
```"""
        else:
            return "Could you be more specific? For example: 'write a function to reverse a string' or 'create a class for a calculator'"

    def general_response(self, message):
        return f"""I understand you're asking about: "{message}"

I can help with:
- Writing code examples
- Explaining programming concepts
- Debugging errors
- Code optimization

Could you provide more details or specific code?"""

assistant = CodeAssistant()

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html().encode())
        elif self.path == '/style.css':
            self.send_response(200)
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            self.wfile.write(self.get_css().encode())
        elif self.path == '/script.js':
            self.send_response(200)
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()
            self.wfile.write(self.get_js().encode())
        else:
            self.send_response(404)
            self.end_headers()
            
    def do_POST(self):
        if self.path == '/chat':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message', '')
            code = data.get('code', '')
            
            response = assistant.generate_response(message, code)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'response': response}).encode())
            
        elif self.path == '/run':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            code = data.get('code', '')
            output = self.run_code(code)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'output': output}).encode())
            
    def run_code(self, code):
        if not code.strip():
            return "No code to run"
            
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
                
            process = subprocess.Popen(
                ['python3', temp_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(timeout=10)
            
            os.unlink(temp_file)
            
            if stderr:
                return f"Error:\n{stderr}"
            return stdout if stdout else "Code executed successfully (no output)"
            
        except subprocess.TimeoutExpired:
            return "Code execution timed out"
        except Exception as e:
            return f"Error: {str(e)}"
            
    def get_html(self):
        return '''<!DOCTYPE html>
<html>
<head>
    <title>AI Coding Assistant</title>
    <link rel="stylesheet" href="/style.css">
</head>
<body>
    <div class="container">
        <div class="left-panel">
            <h2>AI Coding Assistant</h2>
            <div class="chat-container">
                <div id="chat-messages"></div>
                <div class="input-container">
                    <textarea id="user-input" placeholder="Ask me anything about coding..."></textarea>
                    <button onclick="sendMessage()">Send</button>
                </div>
            </div>
        </div>
        
        <div class="right-panel">
            <div class="tabs">
                <button class="tab active" onclick="showTab('editor')">Code Editor</button>
                <button class="tab" onclick="showTab('snippets')">Snippets</button>
                <button class="tab" onclick="showTab('output')">Output</button>
            </div>
            
            <div id="editor" class="tab-content active">
                <div class="toolbar">
                    <button onclick="runCode()">Run Code</button>
                    <button onclick="clearEditor()">Clear</button>
                </div>
                <textarea id="code-editor" placeholder="Write your code here..."></textarea>
            </div>
            
            <div id="snippets" class="tab-content">
                <div class="snippet-controls">
                    <select id="language-select" onchange="updateSnippets()">
                        <option value="Python">Python</option>
                        <option value="JavaScript">JavaScript</option>
                    </select>
                </div>
                <div id="snippets-list"></div>
            </div>
            
            <div id="output" class="tab-content">
                <div id="output-display"></div>
            </div>
        </div>
    </div>
    
    <script src="/script.js"></script>
</body>
</html>'''

    def get_css(self):
        return '''
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background: #1e1e1e;
    color: #d4d4d4;
}

.container {
    display: flex;
    height: 100vh;
}

.left-panel {
    width: 40%;
    background: #252526;
    padding: 20px;
    display: flex;
    flex-direction: column;
}

.right-panel {
    width: 60%;
    background: #1e1e1e;
    display: flex;
    flex-direction: column;
}

h2 {
    color: #4ec9b0;
    margin-bottom: 20px;
}

.chat-container {
    flex: 1;
    display: flex;
    flex-direction: column;
}

#chat-messages {
    flex: 1;
    overflow-y: auto;
    border: 1px solid #3e3e3e;
    padding: 15px;
    background: #2d2d2d;
    border-radius: 5px;
    margin-bottom: 15px;
}

.input-container {
    display: flex;
    gap: 10px;
}

#user-input {
    flex: 1;
    padding: 10px;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    background: #2d2d2d;
    color: #d4d4d4;
    font-family: inherit;
    resize: vertical;
    min-height: 60px;
}

button {
    padding: 10px 20px;
    background: #0e639c;
    color: white;
    border: none;
    border-radius: 5px;
    cursor: pointer;
    font-family: inherit;
}

button:hover {
    background: #1177bb;
}

.tabs {
    display: flex;
    background: #2d2d2d;
    border-bottom: 1px solid #3e3e3e;
}

.tab {
    padding: 12px 20px;
    background: transparent;
    border: none;
    color: #d4d4d4;
    cursor: pointer;
    border-bottom: 3px solid transparent;
}

.tab.active {
    background: #1e1e1e;
    border-bottom-color: #4ec9b0;
}

.tab-content {
    display: none;
    flex: 1;
    padding: 20px;
}

.tab-content.active {
    display: flex;
    flex-direction: column;
}

.toolbar {
    margin-bottom: 10px;
}

.toolbar button {
    margin-right: 10px;
    padding: 8px 16px;
    font-size: 14px;
}

#code-editor {
    flex: 1;
    padding: 15px;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    background: #2d2d2d;
    color: #d4d4d4;
    font-family: 'Consolas', monospace;
    font-size: 14px;
    resize: none;
}

#output-display {
    flex: 1;
    padding: 15px;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    background: #2d2d2d;
    font-family: 'Consolas', monospace;
    font-size: 14px;
    overflow-y: auto;
    white-space: pre-wrap;
}

.message {
    margin-bottom: 15px;
    padding: 10px;
    border-radius: 5px;
    line-height: 1.5;
}

.user-message {
    background: #0e639c;
    color: white;
    margin-left: 50px;
}

.assistant-message {
    background: #3e3e3e;
    color: #d4d4d4;
    margin-right: 50px;
}

.snippet-controls {
    margin-bottom: 15px;
}

#language-select {
    padding: 8px;
    background: #2d2d2d;
    color: #d4d4d4;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
}

.snippet-item {
    padding: 10px;
    margin-bottom: 10px;
    background: #2d2d2d;
    border: 1px solid #3e3e3e;
    border-radius: 5px;
    cursor: pointer;
}

.snippet-item:hover {
    background: #3e3e3e;
}

.snippet-title {
    font-weight: bold;
    color: #4ec9b0;
    margin-bottom: 5px;
}

.snippet-code {
    font-family: 'Consolas', monospace;
    font-size: 12px;
    color: #d4d4d4;
    background: #1e1e1e;
    padding: 8px;
    border-radius: 3px;
    overflow-x: auto;
}

pre {
    background: #2d2d2d;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
    border-left: 4px solid #4ec9b0;
}

code {
    background: #2d2d2d;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: 'Consolas', monospace;
}
'''

    def get_js(self):
        return '''
const snippets = {
    "Python": {
        "Function": "def function_name(param1, param2):\\n    \\\"\\\"\\\"Description\\\"\\\"\\\"\\n    return result",
        "Class": "class ClassName:\\n    def __init__(self, param):\\n        self.param = param\\n    \\n    def method(self):\\n        pass",
        "Try-Except": "try:\\n    # Code here\\n    pass\\nexcept Exception as e:\\n    print(f'Error: {e}')",
        "File Reading": "with open('filename.txt', 'r') as file:\\n    content = file.read()",
        "API Request": "import requests\\nresponse = requests.get('https://api.example.com/data')\\ndata = response.json()"
    },
    "JavaScript": {
        "Function": "function functionName(param1, param2) {\\n    return result;\\n}",
        "Arrow Function": "const functionName = (param1, param2) => {\\n    return result;\\n};",
        "Class": "class ClassName {\\n    constructor(param) {\\n        this.param = param;\\n    }\\n    \\n    method() {\\n        return this.param;\\n    }\\n}",
        "Async Function": "async function fetchData() {\\n    try {\\n        const response = await fetch('url');\\n        const data = await response.json();\\n        return data;\\n    } catch (error) {\\n        console.error('Error:', error);\\n    }\\n}"
    }
};

function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    document.querySelector(`[onclick="showTab('${tabName}')"]`).classList.add('active');
    document.getElementById(tabName).classList.add('active');
}

function sendMessage() {
    const userInput = document.getElementById('user-input');
    const message = userInput.value.trim();
    
    if (!message) return;
    
    addMessage('user', message);
    userInput.value = '';
    
    const code = document.getElementById('code-editor').value;
    
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            code: code
        })
    })
    .then(response => response.json())
    .then(data => {
        addMessage('assistant', data.response);
    })
    .catch(error => {
        addMessage('assistant', 'Sorry, there was an error processing your request.');
    });
}

function addMessage(sender, message) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    // Simple markdown-like formatting
    let formattedMessage = message
        .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*(.+?)\\*/g, '<em>$1</em>')
        .replace(/```([\\s\\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>');
    
    messageDiv.innerHTML = formattedMessage;
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function runCode() {
    const code = document.getElementById('code-editor').value;
    
    if (!code.trim()) {
        document.getElementById('output-display').textContent = 'No code to run';
        showTab('output');
        return;
    }
    
    document.getElementById('output-display').textContent = 'Running code...';
    showTab('output');
    
    fetch('/run', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            code: code
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('output-display').textContent = data.output;
    })
    .catch(error => {
        document.getElementById('output-display').textContent = 'Error running code';
    });
}

function clearEditor() {
    document.getElementById('code-editor').value = '';
}

function updateSnippets() {
    const language = document.getElementById('language-select').value;
    const snippetsList = document.getElementById('snippets-list');
    
    snippetsList.innerHTML = '';
    
    const languageSnippets = snippets[language];
    
    for (const [title, code] of Object.entries(languageSnippets)) {
        const snippetDiv = document.createElement('div');
        snippetDiv.className = 'snippet-item';
        snippetDiv.onclick = () => insertSnippet(code);
        
        snippetDiv.innerHTML = `
            <div class="snippet-title">${title}</div>
            <div class="snippet-code">${code}</div>
        `;
        
        snippetsList.appendChild(snippetDiv);
    }
}

function insertSnippet(code) {
    const editor = document.getElementById('code-editor');
    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    
    editor.value = editor.value.substring(0, start) + code + editor.value.substring(end);
    editor.focus();
    editor.setSelectionRange(start + code.length, start + code.length);
}

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    updateSnippets();
    
    // Add welcome message
    addMessage('assistant', 'Welcome to AI Coding Assistant!\\n\\nI can help you with:\\n• Code explanations and debugging\\n• Writing functions and algorithms\\n• Best practices and optimization\\n• Code review and suggestions\\n\\nType your question and click Send!');
    
    // Enter key to send message
    document.getElementById('user-input').addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && e.ctrlKey) {
            sendMessage();
        }
    });
});
'''

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8000), RequestHandler)
    print("AI Coding Assistant running at http://localhost:8000")
    server.serve_forever()