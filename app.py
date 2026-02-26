import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# UPDATED: The definitive 2026 Router path
API_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity):
    if not HF_TOKEN:
        return "<p style='color:red;'>Error: HF_TOKEN missing in Railway!</p>"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN.strip()}",
        "Content-Type": "application/json"
    }
    
    temp = float(creativity) / 10.0
    
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.3",
        "messages": [
            {"role": "system", "content": "You are a movie expert. Return ONLY an HTML table. No conversation."},
            {"role": "user", "content": f"Recommend 10 movies for a fan of {movies} on {platform}. Table columns: Title, Synopsis, Stars, Streaming."}
        ],
        "temperature": temp,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=110)
        
        if response.status_code != 200:
            return f"<div style='color:orange;'><b>AI Error {response.status_code}:</b><br>{response.text}</div>"
            
        data = response.json()
        
        if 'choices' in data and len(data['choices']) > 0:
            output = data['choices'][0]['message']['content']
            if "<table>" in output:
                return "<table>" + output.split("<table>")[1].split("</table>")[0] + "</table>"
            return f"<div class='results-area'>{output}</div>"
        
        return "<p>AI is warming up. Please click again in 5 seconds!</p>"
    except Exception as e:
        return f"<p>Technical Error: {str(e)}</p>"

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
            background-image: url('/static/space-ai-bg.jpg');
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
        .btn { background: #4da6ff; color: white; padding: 15px; width: 100%; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 20px; }
        .results-area { margin-top: 30px; text-align: left; background: rgba(255,255,255,0.05); padding: 15px; border-radius: 10px; font-size: 0.8rem; border: 1px solid #4da6ff; }
        table { width: 100%; border-collapse: collapse; }
        th, td { border: 1px solid rgba(255,255,255,0.1); padding: 8px; }
        th { color: #4da6ff; }
    </style>
</head>
<body>
    <div class="glass-card">
        <h1>Movie Match Maker AI</h1>
        <form method="POST" id="mainForm">
            <input type="text" name="movie_input" placeholder="Movies you love..." value="{{ user_input }}" required>
            <select name="platform">
                <option value="Anywhere">Anywhere</option>
                <option value="Netflix">Netflix</option>
                <option value="Amazon Prime">Amazon Prime</option>
            </select>
            <label style="display:block; margin-top:15px; font-size:0.9rem;">Creativity: {{ selected_creativity }}</label>
            <input type="range" name="creativity" min="1" max="10" value="{{ selected_creativity }}" style="width:100%;">
            <button type="submit" class="btn" id="submitBtn">Find My Matches</button>
        </form>
        {% if table %}<div class="results-area">{{ table|safe }}</div>{% endif %}
    </div>
    <script>
        document.getElementById('mainForm').onsubmit = function() {
            document.getElementById('submitBtn').innerHTML = "Consulting AI...";
        };
    </script>
</body>
</html>
"""

# --- THE ESSENTIAL ENGINE STARTUP ---
if __name__ == "__main__":
    # This line connects Railway's assigned port to your app
    port = int(os.environ.get("PORT", 8080))
    # This line tells the app to listen to the whole internet (0.0.0.0)
    app.run(host='0.0.0.0', port=port)
