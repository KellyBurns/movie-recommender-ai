import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# UPDATED: The new official Router URL format
API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.3"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity):
    if not HF_TOKEN:
        return "<p style='color:red;'>Error: HF_TOKEN variable is missing in Railway!</p>"
    
    # Updated headers for the Router system
    headers = {
        "Authorization": f"Bearer {HF_TOKEN.strip()}",
        "Content-Type": "application/json",
        "X-Wait-For-Model": "true"
    }
    
    temp = float(creativity) / 10.0
    # Ensuring the prompt is clean and follows Mistral's instruction format
    prompt = f"<s>[INST] Recommend 10 movies for someone who likes: {movies}. Preferred Platform: {platform}. Return ONLY an HTML table with Title, Synopsis, Stars, and Streaming. No chatter. [/INST]"
    
    payload = {
        "inputs": prompt, 
        "parameters": {
            "temperature": temp, 
            "max_new_tokens": 1200
        }
    }
    
    try:
        # Increase timeout to 110s for the new router's processing time
        response = requests.post(API_URL, headers=headers, json=payload, timeout=110)
        
        # This will help us see if it's a token issue or a path issue
        if response.status_code != 200:
            return f"<p style='color:orange;'>AI Router Status {response.status_code}: {response.text}</p>"
            
        data = response.json()
        
        # Router loading state handling
        if isinstance(data, dict) and "estimated_time" in data:
            wait = int(data['estimated_time'])
            return f"<div style='color:#4da6ff;'>The AI is being routed and warmed up (ready in {wait}s). Please click 'Find My Matches' again!</div>"

        # Parsing the generated table
        if isinstance(data, list) and len(data) > 0:
            output = data[0].get('generated_text', "")
            if "<table>" in output:
                return "<table>" + output.split("<table>")[1].split("</table>")[0] + "</table>"
            return f"<p>AI results arrived but were not in table format. Please try one more time!</p>"
        
        return "<p>The AI is ready. Please click the button again to see your results!</p>"
    except Exception as e:
        return f"<p>Connection Error: {str(e)}. Please wait 15 seconds and try again.</p>"

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
        .glass-card { background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(15px); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); width: 420px; max-height: 90vh; overflow-y: auto; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
        h1 { color: #4da6ff; margin-bottom: 5px; }
        input[type="text"], select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #4da6ff; background: rgba(255,255,255,0.1); color: white; box-sizing: border-box; }
        select option { background: #222; color: white; }
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
        {% if table %}<div class="results-area">{{ table|safe }}</div>{% endif %}
    </div>
    <script>
        document.getElementById('mainForm').onsubmit = function() {
            var btn = document.getElementById('submitBtn');
            btn.innerHTML = "Thinking... (Up to 60s)";
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
