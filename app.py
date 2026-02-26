import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Hugging Face Setup
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity):
    if not HF_TOKEN:
        return "Error: HF_TOKEN is missing from Railway Variables."
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
        "X-Wait-For-Model": "true"
    }
    
    temp = float(creativity) / 10.0
    prompt = f"<s>[INST] User likes: {movies}. Platform: {platform}. List 10 movies. Format ONLY as an HTML table with Title, Synopsis, Stars, Streaming. [/INST]"
    
    payload = {"inputs": prompt, "parameters": {"temperature": temp, "max_new_tokens": 1000}}
    
    try:
        # We give the AI a long time to respond, but the app stays 'alive'
        response = requests.post(API_URL, headers=headers, json=payload, timeout=110)
        data = response.json()
        
        if isinstance(data, dict) and "estimated_time" in data:
            return f"The AI is warming up (ready in {int(data['estimated_time'])}s). Please click Find Matches again!"

        if isinstance(data, list) and len(data) > 0:
            output = data[0].get('generated_text', "")
            if "<table>" in output:
                return "<table>" + output.split("<table>")[1].split("</table>")[0] + "</table>"
        
        return "AI is awake! Please click 'Find My Matches' again to see your list."
    except Exception:
        return "The AI took too long. It should be awake now—try clicking again!"

@app.route('/', methods=['GET', 'POST'])
def home():
    table = ""
    user_input = ""
    selected_platform = "Anywhere"
    selected_creativity = "5"

    if request.method == 'POST':
        user_input = request.form.get('movie_input', "")
        selected_platform = request.form.get('platform', "Anywhere")
        selected_creativity = request.form.get('creativity', "5")
        table = query_ai(user_input, selected_platform, selected_creativity)
    
    return render_template_string(HTML_TEMPLATE, table=table, user_input=user_input, selected_platform=selected_platform, selected_creativity=selected_creativity)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Movie Match Maker AI</title>
    <style>
        body { margin: 0; background: #0b0d17; color: white; font-family: 'Segoe UI', sans-serif; height: 100vh; display: flex; justify-content: flex-end; align-items: center; padding-right: 5%; }
        .glass-card { background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(15px); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); width: 420px; max-height: 90vh; overflow-y: auto; text-align: center; }
        h1 { color: #4da6ff; }
        select, input[type="text"] { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid rgba(255,255,255,0.2); background: rgba(255,255,255,0.1); color: white; box-sizing: border-box; }
        select option { background: white; color: black; }
        .btn { background: #4da6ff; color: white; padding: 15px; width: 100%; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 20px; }
        .results-area { margin-top: 30px; text-align: left; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; font-size: 0.8rem; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid rgba(255,255,255,0.1); padding: 8px; }
    </style>
</head>
<body>
    <div class="glass-card">
        <h1>Movie Match Maker AI</h1>
        <form method="POST" id="mainForm">
            <input type="text" name="movie_input" placeholder="Movies you love..." value="{{ user_input }}" required>
            <select name="platform">
                <option value="Anywhere" {% if selected_platform == 'Anywhere' %}selected{% endif %}>Anywhere</option>
                <option value="Netflix" {% if selected_platform == 'Netflix' %}selected{% endif %}>Netflix</option>
                <option value="Disney+" {% if selected_platform == 'Disney+' %}selected{% endif %}>Disney+</option>
            </select>
            <input type="range" name="creativity" min="1" max="10" value="{{ selected_creativity }}" style="width:100%;">
            <button type="submit" class="btn" id="submitBtn">Find My Matches</button>
        </form>
        {% if table %}<div class="results-area">{{ table|safe }}</div>{% endif %}
    </div>
    <script>
        document.getElementById('mainForm').onsubmit = function() {
            var btn = document.getElementById('submitBtn');
            btn.innerHTML = "Consulting AI... (Wait 60s)";
            btn.disabled = true;
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    # RAILWAY CRITICAL: Must use 0.0.0.0 and the PORT variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
