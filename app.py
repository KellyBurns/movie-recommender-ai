import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Stable 2026 Router Path
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity_val):
    if not HF_TOKEN:
        return "<p style='color:red;'>API Token Missing.</p>"
    
    headers = {"Authorization": f"Bearer {HF_TOKEN.strip()}", "Content-Type": "application/json"}
    
    # Map the 1-10 slider to a 0.1 - 1.0 temperature range for the LLM
    temp_setting = max(0.1, min(float(creativity_val) / 10.0, 1.0))
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct:fastest",
        "messages": [
            {
                "role": "system", 
                "content": "You are a precise movie database API. Return ONLY a pure HTML <table>. DO NOT use markdown pipes (|). DO NOT use backticks. Use ONLY English. Provide 10 recommendations."
            },
            {
                "role": "user", 
                "content": f"Create an HTML table for a fan of {movies} on {platform}. Columns: Match %, Title, Year, Synopsis, Stars, Streaming."
            }
        ],
        "temperature": temp_setting,
        "presence_penalty": 0.6,
        "max_tokens": 1500
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        data = response.json()
        output = data['choices'][0]['message']['content']
        clean_html = output.replace("```html", "").replace("```", "").strip()
        
        if "<table" in clean_html:
            return clean_html
        return "<div class='ai-text-fallback'>The AI returned an invalid format. Please try again.</div>"
    except Exception:
        return f"<div style='color:orange;'>Connection glitch. Try one more time!</div>"

@app.route('/')
def landing():
    return render_template_string(LANDING_TEMPLATE)

@app.route('/app', methods=['GET', 'POST'])
def movie_app():
    table = ""
    user_input = ""
    if request.method == 'POST':
        user_input = request.form.get('movie_input', "")
        platform = request.form.get('platform', "Anywhere")
        creativity = request.form.get('creativity', "5")
        table = query_ai(user_input, platform, creativity)
    return render_template_string(APP_TEMPLATE, table=table, user_input=user_input)

# --- UI TEMPLATES ---

LANDING_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Kelly A. Burns | AI Portfolio</title>
    <style>
        body { 
            margin: 0; background: #05070a; background-image: url('/static/space-ai-bg.jpg'); 
            background-size: cover; background-attachment: fixed; color: white; font-family: 'Inter', sans-serif; 
            display: flex; justify-content: flex-end; align-items: center; min-height: 100vh; padding-right: 5%;
        }
        .card { background: rgba(10, 15, 25, 0.85); backdrop-filter: blur(20px); padding: 50px; border-radius: 24px; width: 450px; border: 1px solid rgba(77, 166, 255, 0.2); box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
        .tagline { font-size: 0.9rem; color: #4da6ff; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
        h1 { font-size: 2.5rem; font-weight: 200; margin: 0; }
        .description { font-size: 1.1rem; opacity: 0.7; margin: 15px 0 35px 0; font-weight: 300; }
        .launch-btn { background: linear-gradient(135deg, #4da6ff, #0066cc); color: white; padding: 18px 40px; border-radius: 50px; text-decoration: none; display: inline-block; font-weight: bold; transition: 0.3s; }
        .launch-btn:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(77,166,255,0.4); }
        .copyright { margin-top: 40px; font-size: 0.7rem; opacity: 0.4; letter-spacing: 0.5px; }
    </style>
</head>
<body>
    <div class="card">
        <div class="tagline">AI Portfolio</div>
        <h1>Kelly A. Burns</h1>
        <p class="description">Explorations in AI Development</p>
        <a href="/app" class="launch-btn">Launch Project</a>
        <div class="copyright">© 2026-2027 Kelly A. Burns. All rights reserved.</div>
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
        body { margin: 0; background: #05070a; background-image: url('/static/space-ai-bg.jpg'); background-size: cover; background-attachment: fixed; color: white; font-family: 'Inter', sans-serif; display: flex; justify-content: flex-end; align-items: center; min-height: 100vh; padding-right: 5%; }
        .card { background: rgba(10, 15, 25, 0.85); backdrop-filter: blur(25px); padding: 35px; border-radius: 24px; width: 550px; border: 1px solid rgba(77, 166, 255, 0.3); box-shadow: 0 20px 50px rgba(0,0,0,0.6); max-height: 90vh; overflow-y: auto; }
        .back-link { font-size: 0.7rem; color: #4da6ff; text-decoration: none; opacity: 0.6; display: block; margin-bottom: 10px; }
        h2 { color: #4da6ff; margin: 0; font-weight: 300; }
        .subtitle { font-size: 0.85rem; color: #4da6ff; opacity: 0.7; margin-bottom: 20px; display: block; }
        label { font-size: 0.75rem; opacity: 0.8; display: block; margin-top: 15px; }
        .hint { font-size: 0.7rem; color: #4da6ff; opacity: 0.9; margin-top: 8px; display: block; line-height: 1.4; border-left: 2px solid #4da6ff; padding-left: 10px; }
        input, select { width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.4); color: white; box-sizing: border-box; outline: none; }
        .btn { background: #4da6ff; color: white; padding: 14px; width: 100%; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 15px; }
        #loading { display: none; margin-top: 20px; text-align: center; color: #4da6ff; font-size: 0.9rem; }
        table { width: 100%; border-collapse: collapse; font-size: 0.75rem; margin-top: 20px; }
        th { text-align: left; color: #4da6ff; border-bottom: 1px solid rgba(77,166,255,0.2); padding: 8px; }
        td { padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); vertical-align: top; }
        .range-wrap { display: flex; justify-content: space-between; font-size: 0.65rem; color: #4da6ff; opacity: 0.6; }
    </style>
</head>
<body>
    <div class="card">
        <a href="/" class="back-link">← Portfolio Home</a>
        <h2>Movie Match Maker [BETA]</h2>
        <span class="subtitle">Let's find your next favorite film...</span>
        <form method="POST" action="/app">
            <label>What movies or actors do you love?</label>
            <input type="text" name="movie_input" placeholder="e.g. Inception, Heat, Sandra Bullock" value="{{ user_input }}" required>
            <span class="hint"><b>Pro Tip:</b> The more films/actors you provide, the better the AI can triangulate your specific taste in pacing, cinematography, and themes.</span>
            
            <label style="margin-top: 20px;">Model Temperature (Creativity)</label>
            <input type="range" name="creativity" min="1" max="10" value="5">
            <div class="range-wrap">
                <span>0.1 (Precise)</span>
                <span>1.0 (Creative)</span>
            </div>
            <span class="hint" style="border-color: #ff9900; opacity: 0.7;"><b>Parameter Note:</b> Adjusting this slider modifies the model's <b>sampling temperature</b> to control the variance of the recommendation engine.</span>

            <label style="margin-top: 15px;">Streaming Service</label>
            <select name="platform">
                <option value="Anywhere">Anywhere</option>
                <option value="Netflix">Netflix</option>
                <option value="Amazon Prime">Amazon Prime</option>
                <option value="HBO Max">HBO Max</option>
            </select>
            <button type="submit" class="btn">Find My Matches</button>
        </form>
        <div id="loading">Consulting the Multiverse...</div>
        {% if table %}<div id="results">{{ table|safe }}</div>{% endif %}
    </div>
    <script>
        document.querySelector('form').onsubmit = function() {
            document.getElementById('loading').style.display = 'block';
            if(document.getElementById('results')) document.getElementById('results').style.opacity = '0.3';
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
