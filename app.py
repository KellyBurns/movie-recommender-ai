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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@200;400;700&display=swap');
        


body { 
            margin: 0; 
            background-color: #05070a; /* Fallback color */
            color: white; 
            font-family: 'Inter', sans-serif; 
            display: flex; 
            justify-content: flex-end; 
            align-items: center; 
            min-height: 100vh; 
            padding-right: 5%;
            
            /* Hard-coded to the static folder */
            background-image: url('/static/space-ai-bg.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }

        
        .card { 
            background: rgba(10, 15, 25, 0.8); 
            backdrop-filter: blur(10px);
            padding: 40px; 
            border-radius: 24px; 
            width: 550px; 
            border: 1px solid rgba(77, 166, 255, 0.2); 
            box-shadow: 0 20px 50px rgba(0,0,0,0.5);
        }

        h1 { font-size: 3rem; font-weight: 200; margin: 0 0 10px 0; letter-spacing: -1px; }
        .tagline { color: #4da6ff; font-weight: 400; letter-spacing: 2px; text-transform: uppercase; font-size: 0.8rem; margin-bottom: 30px; }

        .launch-btn { 
            background: linear-gradient(135deg, #4da6ff, #0066cc); 
            color: white; 
            padding: 16px 35px; 
            border-radius: 50px; 
            text-decoration: none; 
            display: inline-block; 
            font-weight: bold; 
            margin-bottom: 40px;
            transition: transform 0.2s;
        }
        .launch-btn:hover { transform: scale(1.05); }

        .tech-section { 
            border-top: 1px solid rgba(255, 255, 255, 0.1); 
            padding-top: 25px;
        }

        h2 { font-size: 1.2rem; color: #4da6ff; margin-bottom: 15px; font-weight: 700; }
        h3 { font-size: 0.9rem; margin: 20px 0 8px 0; color: rgba(255,255,255,0.9); }
        
        p { 
            font-size: 0.85rem; 
            line-height: 1.6; 
            color: rgba(255, 255, 255, 0.7); 
            margin-bottom: 15px; 
        }

        .audit-highlight {
            background: rgba(77, 166, 255, 0.1);
            border-left: 3px solid #4da6ff;
            padding: 10px 15px;
            font-style: italic;
            margin: 15px 0;
        }

        .footer {
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.05);
            font-size: 0.75rem;
            opacity: 0.6;
        }
    </style>
</head>
<body>
    <div class="card">
        <h1>Kelly A. Burns</h1>
        <p class="description">Explorations in AI Development</p>
        
        <a href="/app" class="launch-btn">Launch Project</a>

        <div class="tech-section">
            <h2>Technical Architecture</h2>
            
            <h3>Human-In-The-Loop Collaboration</h3>
            <p>I architected this solo project through an AI-augmented development process to accelerate prototyping. By employing Gemini 3 Flash for high-order logic, I bridged the gap between back-end infrastructure and front-end user experience.</p>
            <p> I maintained a strict manual audit layer, correcting recursive context-loss issues—such as repeated dropping of environment port configurations and prompt logic—to ensure system stability.
            </p>

            <h3>Tech Stack</h3>
            <p>Built on a <b>Python/Flask</b> micro-framework. Version control is managed via <b>GitHub</b> with an automated <b>CI/CD pipeline</b> deploying to a cloud-native <b>Railway</b> environment. All UI/UX is proprietary design.</p>

            <h3>The Engine (Llama 3.2)</h3>
            <p>Utilizes Llama 3.2 via <b>Hugging Face API</b> for advanced zero-shot reasoning. To manage stochastic randomness and prevent hallucinations, I implemented a <b>Temperature Parameter (0.1 - 1.0)</b>, allowing user-level control over prediction probability distributions.</p>
        </div>


    <div class="footer">
        Palm Desert, CA | <a href="mailto:KBurnsDirect@gmail.com" target="_blank" style="color:#4da6ff; text-decoration:none;">KBurnsDirect@gmail.com</a><br>
        LinkedIn: <a href="https://www.linkedin.com/in/kellyburns-pm" target="_blank" style="color:#4da6ff; text-decoration:none;">KellyBurns-PM</a><br>
        &copy; 2026 Kelly A. Burns. All Rights Reserved. Verified Project.
    </div>

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
