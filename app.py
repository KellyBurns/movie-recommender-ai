import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Hugging Face Setup
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity):
    if not HF_TOKEN:
        return "<p style='color:red;'>Error: HF_TOKEN is missing from Railway Variables.</p>"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN}",
        "Content-Type": "application/json",
        "X-Wait-For-Model": "true"
    }
    
    temp = float(creativity) / 10.0
    # Refined prompt for even stricter output
    prompt = f"<s>[INST] User likes: {movies}. Platform: {platform}. List 10 movies. Format ONLY as an HTML table with Title, Synopsis, Stars, Streaming. No chatter. [/INST]"
    
    payload = {"inputs": prompt, "parameters": {"temperature": temp, "max_new_tokens": 1000}}
    
    try:
        # We allow 110 seconds for the model to wake up
        response = requests.post(API_URL, headers=headers, json=payload, timeout=110)
        data = response.json()
        
        # Scenario A: Model is still loading
        if isinstance(data, dict) and "estimated_time" in data:
            wait = int(data['estimated_time'])
            return f"<div style='color:#4da6ff; font-weight:bold;'>The AI is waking up! It needs about {wait} more seconds. Please click the button again in a moment.</div>"

        # Scenario B: Success!
        if isinstance(data, list) and len(data) > 0:
            output = data[0].get('generated_text', "")
            if "<table>" in output:
                return "<table>" + output.split("<table>")[1].split("</table>")[0] + "</table>"
            return "<p>AI results arrived but were messy. Please try clicking 'Find My Matches' again.</p>"
        
        return "<p>The AI is ready now! Please click the button one more time to see your matches.</p>"
    except Exception as e:
        return f"<p>Connection timed out. The AI is still loading—please wait 10 seconds and click again!</p>"

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
        body { 
            margin: 0; 
            background: #0b0d17; 
            /* Fix for BG image - ensure this file exists in /static/ */
            background-image: url('https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?q=80&w=2072&auto=format&fit=crop');
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
            background-size: cover; 
            color: white; 
            font-family: 'Segoe UI', sans-serif; 
            height: 100vh; 
            display: flex; 
            justify-content: flex-end; 
            align-items: center; 
            padding-right: 5%; 
        }
        .glass-card { background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(15px); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); width: 420px; max-height: 90vh; overflow-y: auto; text-align: center; }
        h1 { color: #4da6ff; margin-bottom: 5px; }
        input[type="text"], select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #4da6ff; background: rgba(255,255,255,0.1); color: white; box-sizing: border-box; }
        select option { background: #222; color: white; }
        .btn { background: #4da6ff; color: white; padding: 15px; width: 100%; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 20px; transition: 0.3s; }
        .btn:hover { background: #007bff; }
        .results-area { margin-top: 30px; text-align: left; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; font-size: 0.8rem; border: 1px solid #4da6ff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid rgba(255,255,255,0.1); padding: 8px; }
        th { color: #4da6ff; }
    </style>
</head>
<body>
    <div class="glass-card">
        <h1>Movie Match Maker AI</h1>
        <p style="opacity: 0.7;">Your AI Cinema Concierge</p>
        <form method="POST" id="mainForm">
            <input type="text" name="movie_input" placeholder="Movies you love..." value="{{ user_input }}" required>
            <select name="platform">
                <option value="Anywhere" {% if selected_platform == 'Anywhere' %}selected{% endif %}>Anywhere</option>
                <option value="Netflix" {% if selected_platform == 'Netflix' %}selected{% endif %}>Netflix</option>
                <option value="Amazon Prime" {% if selected_platform == 'Amazon Prime' %}selected{% endif %}>Amazon Prime</option>
                <option value="HBO Max" {% if selected_platform == 'HBO Max' %}selected{% endif %}>HBO Max</option>
                <option value="Disney+" {% if selected_platform == 'Disney+' %}selected{% endif %}>Disney+</option>
            </select>
            <label style="display:block; margin-top:15px; font-size:0.9rem;">Creativity: {{ selected_creativity }}</label>
            <input type="range" name="creativity" min="1" max="10" value="{{ selected_creativity }}" style="width:100%;">
            <button type="submit" class="btn" id="submitBtn">Find My Matches</button>
        </form>
        {% if table %}
        <div class="results-area">
            {{ table|safe }}
        </div>
        {% endif %}
    </div>
    <script>
        document.getElementById('mainForm').onsubmit = function() {
            var btn = document.getElementById('submitBtn');
            btn.innerHTML = "Consulting AI... (Wait 60s)";
            // We removed 'disabled' so you can click it again if it takes too long
        };
    </script>
</body>
</html>
