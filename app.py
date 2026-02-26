import os
import requests
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# 2026 Stable Router Path
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity):
    if not HF_TOKEN:
        return "<p style='color:red;'>Error: HF_TOKEN missing!</p>"
    headers = {"Authorization": f"Bearer {HF_TOKEN.strip()}", "Content-Type": "application/json"}
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct:fastest",
        "messages": [
            {"role": "system", "content": "You are a precise movie database API. Return ONLY a valid HTML table. NO MARKDOWN. NO CONVERSATION. ORDER: Match %, Title, Year, Synopsis, Stars, Streaming. Ensure Synopsis is in English only."},
            {"role": "user", "content": f"Recommend 10 movies for a fan of {movies} on {platform}. Format: <table> tags only."}
        ],
        "temperature": 0.7,
        "presence_penalty": 0.5,
        "max_tokens": 1400
    }
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        data = response.json()
        output = data['choices'][0]['message']['content']
        if "<table>" in output:
            table_html = output.split("<table>")[1].split("</table>")[0]
            return '<table id="movieTable">' + table_html + '</table>'
        return "<div class='ai-text-fallback'>The AI had a glitch. Please refresh and try again.</div>"
    except:
        return "<div style='color:orange;'>AI is recalibrating. Try one more time!</div>"

@app.route('/')
def landing():
    return render_template_string(LANDING_TEMPLATE)

@app.route('/app', methods=['GET', 'POST'])
def movie_app():
    table = ""
    user_input = ""
    if request.method == 'POST':
        user_input = request.form.get('movie_input', "")
        table = query_ai(user_input, request.form.get('platform', "Anywhere"), "7")
    return render_template_string(APP_TEMPLATE, table=table, user_input=user_input)

# --- TEMPLATES ---

LANDING_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kelly A. Burns | AI Portfolio</title>
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
            padding: 50px; border-radius: 24px; width: 500px; 
            border: 1px solid rgba(77, 166, 255, 0.3); 
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            text-align: left;
        }
        h1 { font-size: 2.8rem; font-weight: 200; letter-spacing: -1px; margin: 0; color: white; }
        .tagline { font-size: 1.1rem; color: #4da6ff; margin-bottom: 5px; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; }
        .description { font-size: 1.1rem; opacity: 0.7; margin-bottom: 40px; font-weight: 300; line-height: 1.6; }
        .launch-btn { 
            background: linear-gradient(135deg, #4da6ff, #0066cc); color: white; 
            padding: 18px 45px; font-size: 1rem; border-radius: 50px; border: none;
            cursor: pointer; transition: 0.3s; text-decoration: none; display: inline-block; font-weight: bold;
        }
        .launch-btn:hover { transform: translateY(-2px); box-shadow: 0 10px 20px rgba(77,166,255,0.4); }
        .copyright { margin-top: 50px; font-size: 0.7rem; opacity: 0.4; letter-spacing: 1px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="tagline">AI Portfolio</div>
        <h1>Kelly A. Burns</h1>
        <p class="description">Explorations in AI Development</p>
        <a href="/app" class="launch-btn">Launch Project</a>
        <div class="copyright">All work copyright 2026-2030</div>
    </div>
</body>
</html>
"""

APP_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Movie Match Maker [BETA]</title>
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
            padding: 35px; border-radius: 24px; width: 550px; 
            border: 1px solid rgba(77, 166, 255, 0.3); 
            box-shadow: 0 20px 50px rgba(0,0,0,0.6);
            max-height: 90vh; overflow-y: auto;
        }
        .back-link { font-size: 0.7rem; color: #4da6ff; text-decoration: none; opacity: 0.6; display: block; margin-bottom: 10px; }
        h2 { color: #4da6ff; margin: 0; font-weight: 300; letter-spacing: 1px; }
        .subtitle { font-size: 0.9rem; color: #4da6ff; opacity: 0.7; margin-bottom: 25px; display: block; }
        label { font-size: 0.8rem; opacity: 0.8; display: block; margin-top: 15px; }
        .hint { font-size: 0.75rem; color: #4da6ff; opacity: 0.9; margin-top: 10px; display: block; line-height: 1.4; border-left: 2px solid #4da6ff; padding-left: 10px; }
        input, select { width: 100%; padding: 14px; margin: 8px 0; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.4); color: white; font-size: 1rem; box-sizing: border-box; outline: none; }
        .btn { background: linear-gradient(135deg, #4da6ff, #0066cc); color: white; padding: 16px; width: 100%; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 15px; }
        #loading-state { display: none; margin-top: 20px; text-align: center; }
        .spinner { width: 24px; height: 24px; border: 3px solid rgba(77,166,255,0.2); border-top: 3px solid #4da6ff; border-radius: 50%; animation: spin 1s linear infinite; display: inline-block; vertical-align: middle; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; table-layout: fixed; margin-top: 20px; }
        th { text-align: left; color: #4da6ff; padding: 10px 5px; border-bottom: 1px solid rgba(77, 166, 255, 0.2); }
        td { padding: 10px 5px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #ddd; vertical-align: top; }
        td:first-child { font-weight: bold; color: #4da6ff; }
    </style>
</head>
<body>
    <div class="card">
        <a href="/" class="back-link">← Portfolio Home</a>
        <h2>Movie Match Maker [BETA]</h2>
        <span class="subtitle">Let's find your next favorite film...</span>
        <form method="POST" id="movieForm">
            <label>What movies or actors do you love?</label>
            <input type="text" name="movie_input" placeholder="e.g. Inception, Heat, Sandra Bullock" value="{{ user_input }}" required>
            <span class="hint"><b>Pro Tip:</b> The more films and/or actors you provide, the better the AI can triangulate your specific taste in pacing, cinematography, and themes.</span>
            <label style="margin-top: 20px;">Streaming Service</label>
            <select name="platform">
                <option value="Anywhere">Anywhere</option>
                <option value="Netflix">Netflix</option>
                <option value="Amazon Prime">Amazon Prime</option>
                <option value="HBO Max">HBO Max</option>
            </select>
            <button type="submit" class="btn" id="submitBtn">Find My Matches</button>
        </form>
        <div id="loading-state"><div class="spinner"></div> <span style="color:#4da6ff">Analyzing taste vectors...</span></div>
        {% if table %}<div id="resultsTable">{{ table|safe }}</div>{% endif %}
    </div>
    <script>
        document.getElementById('movieForm').onsubmit = function() {
            document.getElementById('submitBtn').style.display = 'none';
            document.getElementById('loading-state').style.display = 'block';
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
