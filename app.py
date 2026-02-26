import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 2026 Stable Router Path
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity):
    if not HF_TOKEN:
        return "<p style='color:red;'>Error: HF_TOKEN missing in Railway!</p>"
    
    headers = {"Authorization": f"Bearer {HF_TOKEN.strip()}", "Content-Type": "application/json"}
    
    # Scale 1-10 to 0.1-1.0
    temp = float(creativity) / 10.0
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct:fastest",
        "messages": [
            {
                "role": "system", 
                "content": "You are a movie expert. Return ONLY an HTML table. Columns MUST be: Year, Title, Synopsis, Stars, Streaming. No extra text."
            },
            {
                "role": "user", 
                "content": f"Recommend 10 movies for a fan of {movies} on {platform}."
            }
        ],
        "temperature": temp,
        "max_tokens": 1200
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return f"<div style='color:orange;'>The AI is busy. Please try again in 10 seconds!</div>"
            
        data = response.json()
        output = data['choices'][0]['message']['content']
        
        if "<table>" in output:
            return "<table>" + output.split("<table>")[1].split("</table>")[0] + "</table>"
        return f"<div class='ai-text-fallback'>{output}</div>"
    except Exception as e:
        return f"<p>Connection Error: {str(e)}</p>"

@app.route('/', methods=['GET', 'POST'])
def home():
    table = ""
    user_input = ""
    selected_platform = "Select Streaming Service"
    
    if request.method == 'POST':
        user_input = request.form.get('movie_input', "")
        selected_platform = request.form.get('platform', "Anywhere")
        p_query = "Anywhere" if selected_platform == "Select Streaming Service" else selected_platform
        table = query_ai(user_input, p_query, request.form.get('creativity', "7"))
    
    return render_template_string(HTML_TEMPLATE, table=table, user_input=user_input)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Movie Match Maker</title>
    <style>
        body { 
            margin: 0; background: #05070a; 
            background-image: url('/static/space-ai-bg.jpg'); 
            background-size: cover; background-attachment: fixed; background-position: center;
            color: white; font-family: 'Inter', sans-serif; 
            display: flex; justify-content: flex-end; align-items: center; min-height: 100vh; padding-right: 5%;
        }
        .card { 
            background: rgba(10, 15, 25, 0.85); backdrop-filter: blur(25px); 
            padding: 35px; border-radius: 24px; width: 460px; 
            border: 1px solid rgba(77, 166, 255, 0.3); 
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            max-height: 90vh; overflow-y: auto;
        }
        h2 { color: #4da6ff; margin-bottom: 0px; font-weight: 300; letter-spacing: 1px; }
        .subtitle { font-size: 0.9rem; color: #4da6ff; opacity: 0.7; margin-bottom: 25px; display: block; }
        label { font-size: 0.8rem; opacity: 0.8; display: block; margin-top: 15px; }
        input, select { 
            width: 100%; padding: 14px; margin: 8px 0; border-radius: 12px; 
            border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.4); 
            color: white; font-size: 1rem; box-sizing: border-box;
        }
        .range-labels { display: flex; justify-content: space-between; font-size: 0.7rem; color: #4da6ff; margin-bottom: 10px; }
        .btn { 
            background: linear-gradient(135deg, #4da6ff, #0066cc); color: white; 
            padding: 16px; width: 100%; border: none; border-radius: 50px; 
            font-weight: bold; cursor: pointer; margin-top: 15px; transition: 0.3s;
        }
        #loading-state { display: none; margin-top: 20px; text-align: center; }
        .spinner { 
            width: 24px; height: 24px; border: 3px solid rgba(77,166,255,0.2); 
            border-top: 3px solid #4da6ff; border-radius: 50%; 
            animation: spin 1s linear infinite; display: inline-block; vertical-align: middle;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .results { margin-top: 25px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; }
        th { text-align: left; color: #4da6ff; padding: 10px 5px; border-bottom: 1px solid rgba(77, 166, 255, 0.2); }
        td { padding: 10px 5px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #ddd; vertical-align: top; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Movie Match Maker</h2>
        <span class="subtitle">Your AI Film Concierge</span>
        <form method="POST" id="movieForm">
            <label>What movies do you love?</label>
            <input type="text" name="movie_input" placeholder="Enter movies you like (e.g. Inception, Heat)" value="{{ user_input }}" required>
            <label>Where are you watching?</label>
            <select name="platform">
                <option selected disabled>Select Streaming Service</option>
                <option value="Anywhere">Anywhere</option>
                <option value="Netflix">Netflix</option>
                <option value="Amazon Prime">Amazon Prime</option>
                <option value="HBO Max">HBO Max</option>
                <option value="Disney+">Disney+</option>
                <option value="Hulu">Hulu</option>
            </select>
            <label>Creativity Level</label>
            <input type="range" name="creativity" min="1" max="10" value="7">
            <div class="range-labels">
                <span>1: Predictable Hits (Accurate)</span>
                <span>10: Deep Cuts (Creative)</span>
            </div>
            <button type="submit" class="btn" id="submitBtn">Find My Matches</button>
        </form>
        <div id="loading-state">
            <div class="spinner"></div>
            <span style="margin-left: 10px; font-size: 0.9rem; color: #4da6ff;">Consulting the Multiverse...</span>
        </div>
        {% if table %}
        <div class="results" id="resultsTable">
            {{ table|safe }}
        </div>
        {% endif %}
    </div>
    <script>
        const form = document.getElementById('movieForm');
        const btn = document.getElementById('submitBtn');
        const loading = document.getElementById('loading-state');
        const results = document.getElementById('resultsTable');
        form.onsubmit = function() {
            btn.style.display = 'none';
            loading.style.display = 'block';
            if (results) { results.style.opacity = '0.2'; }
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
