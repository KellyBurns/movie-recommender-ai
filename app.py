import os
import requests
from flask import Flask, request, render_template_string

app = Flask(name)

Production API Configuration
API_URL = ""
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity_val):
if not HF_TOKEN:
return "API Token Missing."

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

LANDING_TEMPLATE = """

<!DOCTYPE html>

<html>
<head>
<title>Kelly A. Burns | AI Portfolio</title>
<style>
body { margin: 0; background: #05070a; background-image: url('/static/space-ai-bg.jpg'); background-size: cover; background-attachment: fixed; color: white; font-family: sans-serif; display: flex; justify-content: flex-end; align-items: center; min-height: 100vh; padding-right: 5%; }
.card { background: rgba(10, 15, 25, 0.85); backdrop-filter: blur(20px); padding: 40px; border-radius: 24px; width: 480px; border: 1px solid rgba(77, 166, 255, 0.2); }
.tech-stack { border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; font-size: 0.75rem; opacity: 0.6; }
.launch-btn { background: #4da6ff; color: white; padding: 15px 30px; border-radius: 50px; text-decoration: none; display: inline-block; font-weight: bold; margin: 20px 0; }
</style>
</head>
<body>
<div class="card">
<h1>Kelly A. Burns</h1>
<p>Explorations in AI Development</p>
<a href="/app" class="launch-btn">Launch Project</a>
<div class="tech-stack">
<h3>Technical Architecture</h3>
<p>Solo project architected via <b>Gemini 3 Flash</b>. Powered by <b>Llama 3.2</b>. Deployed on Railway.</p>
</div>
<p style="font-size: 0.7rem; opacity: 0.4;">© 2026-2027 Kelly A. Burns. All rights reserved.</p>
</div>
</body>
</html>
"""

APP_TEMPLATE = """

<!DOCTYPE html>

<html>
<head>
<title>Movie Match Maker</title>
<style>
body { margin: 0; background: #05070a; background-image: url('/static/space-ai-bg.jpg'); background-size: cover; background-attachment: fixed; color: white; font-family: sans-serif; display: flex; justify-content: flex-end; align-items: center; min-height: 100vh; padding-right: 5%; }
.card { background: rgba(10, 15, 25, 0.9); padding: 30px; border-radius: 20px; width: 550px; max-height: 90vh; overflow-y: auto; }
input, select, .btn { width: 100%; padding: 12px; margin: 10px 0; border-radius: 10px; }
.btn { background: #4da6ff; color: white; font-weight: bold; cursor: pointer; border: none; }
table { width: 100%; font-size: 0.7rem; border-collapse: collapse; margin-top: 20px; }
td, th { padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.1); text-align: left; }
</style>
</head>
<body>
<div class="card">
<a href="/" style="color: #4da6ff; text-decoration: none; font-size: 0.8rem;">← Back</a>
<h2>Movie Match Maker</h2>
<form method="POST">
<input type="text" name="movie_input" placeholder="Favorite movies..." value="{{ user_input }}" required>
<input type="range" name="creativity" min="1" max="10" value="5">
<select name="platform"><option>Netflix</option><option>Anywhere</option></select>
<button type="submit" class="btn">Find My Matches</button>
</form>
{% if table %}<div id="results">{{ table|safe }}</div>{% endif %}
</div>
</body>
</html>
"""

if name == "main":
port = int(os.environ.get("PORT", 8080))
app.run(host='0.0.0.0', port=port)
