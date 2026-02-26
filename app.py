import os
import requests
from flask import Flask, request, render_template_string

app = Flask(name)

# Production API Configuration
API_URL = ""
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity_val):
if not HF_TOKEN:
return "<p style='color:red;'>API Token Missing.</p>"

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

--- UI TEMPLATES ---
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
.card { background: rgba(10, 15, 25, 0.85); backdrop-filter: blur(20px); padding: 50px; border-radius: 24px; width: 480px; border: 1px solid rgba(77, 166, 255, 0.2); box-shadow: 0 20px 50px rgba(0,0,0,0.5); }
.tagline { font-size: 0.9rem; color: #4da6ff; letter-spacing: 2px; text-transform: uppercase; font-weight: 600; margin-bottom: 5px; }
h1 { font-size: 2.5rem; font-weight: 200; margin: 0; }
.description { font-size: 1.1rem; opacity: 0.7; margin: 15px 0 35px 0; font-weight: 300; }
.launch-btn { background: linear-gradient(135deg, #4da6ff, #0066cc); color: white; padding: 18px 40px; border-radius: 50px; text-decoration: none; display: inline-block; font-weight: bold; transition: 0.3s; margin-bottom: 20px; }
.launch-btn:hover { transform: scale(1.05); box-shadow: 0 0 20px rgba(77,166,255,0.4); }
.tech-stack { border-top: 1px solid rgba(255, 255, 255, 0.1); margin-top: 30px; padding-top: 20px; text-align: left; }
.tech-stack h3 { font-size: 0.7rem; color: #4da6ff; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 12px; }
.tech-stack p { font-size: 0.75rem; line-height: 1.6; opacity: 0.7; font-weight: 300; margin-bottom: 12px; }
.tech-stack b { color: #fff; font-weight: 500; }
.copyright { margin-top: 30px; font-size: 0.7rem; opacity: 0.4; letter-spacing: 0.5px; }
</style>
</head>
<body>
<div class="card">
<div class="tagline">AI Portfolio</div>
<h1>Kelly A. Burns</h1>
<p class="description">Explorations in AI Development</p>
<a href="/app" class="launch-btn">Launch Project</a>
<div class="tech-stack">
<h3>Technical Architecture</h3>
<p>This project was architected through a collaborative development process using <b>Gemini 3 Flash</b>.</p>
<p>The recommendation engine utilizes the <b>Llama 3.2</b> model. To mitigate <b>stochastic randomness</b> and prevent hallucinations, the application exposes a <b>Temperature Parameter</b>. By adjusting the sampling temperature (0.1 to 1.0), the user directly controls the probability distribution of predictions.</p>
<p>Built on <b>Python/Flask</b> and deployed via <b>Railway</b>.</p>
</div>
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
label { font-size: 0.75rem; opacity: 0.8; display: block; margin-top: 15px; }
input, select { width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.4); color: white; box-sizing: border-box; }
.btn { background: #4da6ff; color: white; padding: 14px; width: 100%; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 15px; }
#loading { display: none; margin-top: 20px; text-align: center; color: #4da6ff; }
table { width: 100%; border-collapse: collapse; font-size: 0.75rem; margin-top: 20px; }
th { text-align: left; color: #4da6ff; border-bottom: 1px solid rgba(77,166,255,0.2); padding: 8px; }
td { padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); }
</style>
</head>
<body>
<div class="card">
<a href="/" class="back-link">← Portfolio Home</a>
<h2>Movie Match Maker [BETA]</h2>
<form method="POST" action="/app">
<label>What movies or actors do you love?</label>
<input type="text" name="movie_input" value="{{ user_input }}" required>
<label>Creativity (Temperature)</label>
<input type="range" name="creativity" min="1" max="10" value="5">
<select name="platform">
<option value="Anywhere">Anywhere</option>
<option value="Netflix">Netflix</option>
</select>
<button type="submit" class="btn">Find My Matches</button>
</form>
<div id="loading">Consulting the Multiverse...</div>
{% if table %}<div id="results">{{ table|safe }}</div>{% endif %}
</div>
<script>
document.querySelector('form').onsubmit = function() { document.getElementById('loading').style.display = 'block'; };
</script>
</body>
</html>
"""

if name == "main":
port = int(os.environ.get("PORT", 8080))
app.run(host='0.0.0.0', port=port)
