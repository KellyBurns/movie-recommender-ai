import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Hugging Face Setup
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {
    "Authorization": f"Bearer {os.environ.get('HF_TOKEN')}",
    "Content-Type": "application/json",
    "X-Wait-For-Model": "true"
}

def query_ai(movies, platform, creativity):
    if not movies or len(movies.strip()) < 2:
        return "Please enter at least one movie title."

    temp = float(creativity) / 10.0
    prompt = f"[INST] User likes: {movies}. Preferred Platform: {platform}. Provide 10 recommendations. Format ONLY as an HTML table with columns: Title, Synopsis, Top 3 Stars, Streaming On. [/INST]"
    
    payload = {
        "inputs": prompt, 
        "parameters": {"temperature": temp, "max_new_tokens": 1200}
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            output = data[0].get('generated_text', "")
            if "<table>" in output:
                return "<table>" + output.split("<table>")[1].split("</table>")[0] + "</table>"
            return "The AI woke up but didn't build the table correctly. Click find again!"
        
        return "The AI is still waking up. Please click 'Find My Matches' again in 10 seconds!"
    
    except Exception:
        return "Connection timed out. The AI is still loading—please click the button again."

@app.route('/', methods=['GET', 'POST'])
def home():
    table = ""
    # We capture these so we can send them back to the form
    user_input = ""
    selected_platform = "Anywhere"
    selected_creativity = "5"

    if request.method == 'POST':
        user_input = request.form.get('movie_input', "")
        selected_platform = request.form.get('platform', "Anywhere")
        selected_creativity = request.form.get('creativity', "5")
        table = query_ai(user_input, selected_platform, selected_creativity)
    
    return render_template_string(
        HTML_TEMPLATE, 
        table=table, 
        user_input=user_input, 
        selected_platform=selected_platform,
        selected_creativity=selected_creativity
    )

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Movie Match Maker AI</title>
    <style>
        body { margin: 0; background: url('/static/space-ai-bg.jpg') no-repeat center center fixed; background-size: cover; color: white; font-family: 'Segoe UI', sans-serif; height: 100vh; display: flex; justify-content: flex-end; align-items: center; padding-right: 5%; }
        .glass-card { background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); width: 450px; max-height: 90vh; overflow-y: auto; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #4da6ff; margin-bottom: 5px; }
        select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #4da6ff; background: rgba(255,255,255,0.1); color: white; cursor: pointer; }
        select option { background-color: white !important; color: black !important; }
        input[type="text"] { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; background: rgba(255,255,255,0.1); color: white; box-sizing: border-box; }
        .btn { background: #4da6ff; color: white; padding: 15px; width: 100%; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 20px; }
        .btn:disabled { background: #555; cursor: not-allowed; }
        .results-area { margin-top: 30px; text-align: left; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 15px; }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
        th, td { border: 1px solid rgba(255,255,255,0.1); padding: 8px; text-align: left; }
        th { color: #4da6ff; background: rgba(77, 166, 255, 0.1); }
    </style>
</head>
<body>
    <div class="glass-card">
        <h1>Movie Match Maker AI</h1>
        <p style="opacity: 0.7;">Finding your next favorite film...</p>
        
        <form method="POST" id="mainForm">
            <input type="text" name="movie_input" placeholder="Enter movies you love..." value="{{ user_input }}" required>
            
            <select name="platform">
                <option value="Anywhere" {% if selected_platform == 'Anywhere' %}selected{% endif %}>Anywhere</option>
                <option value="Netflix" {% if selected_platform == 'Netflix' %}selected{% endif %}>Netflix</option>
                <option value="Amazon Prime" {% if selected_platform == 'Amazon Prime' %}selected{% endif %}>Amazon Prime</option>
                <option value="HBO Max" {% if selected_platform == 'HBO Max' %}selected{% endif %}>HBO Max</option>
                <option value="Disney+" {% if selected_platform == 'Disney+' %}selected{% endif %}>Disney+</option>
                <option value="Hulu" {% if selected_platform == 'Hulu' %}selected{% endif %}>Hulu</option>
            </select>
            
            <label style="display:block; margin-top:15px; font-size:0.9rem;">Creativity Level: {{ selected_creativity }}</label>
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
            btn.innerHTML = "Consulting the AI... (Up to 60s)";
            btn.disabled = true;
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
