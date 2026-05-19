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
    
    # Map the 1-10 slider to a 0.1 - 1.0 temperature range
    slider_num = int(creativity_val)
    temp_setting = max(0.1, min(float(slider_num) / 10.0, 1.0))
    
    # DYNAMIC LOGIC: Shift the prompt's instructions based on the slider value to force variety
    if slider_num <= 3:
        creativity_instruction = (
            "Focus on the most direct, highly probable, and mathematically closest cinematic matches. "
            "Prioritize movies that share the exact genre, direct tone, and obvious structural styles of the input."
        )
    elif 4 <= slider_num <= 7:
        creativity_instruction = (
            "Introduce moderate variety. Look for films with overlapping directors, cinematographers, or "
            "sub-genres. Blend obvious choices with slightly unexpected but highly artistic alternatives."
        )
    else:
        creativity_instruction = (
            "CRITICAL: Unleash maximum variety and out-of-the-box creativity. AVOID the most obvious blockbusters. "
            "Instead, recommend hidden gems, cult classics, indie masterpieces, or films with unexpected thematic links, "
            "unconventional narrative styles, or abstract philosophical connections to the input. Be boldly creative."
        )

    # Base system prompt embedded with our dynamic creativity instruction
    system_content = (
        f"You are an expert movie database API and recommendation engine. "
        f"Your first job is to validate the user's input. If the input consists of completely made-up gibberish, "
        f"random keyboard typing, or entirely fictional titles/people that do not exist in reality, you MUST "
        f"return exactly the word: NOT_FOUND. Do not return anything else.\n\n"
        f"CRITICAL VALIDATION RULE: If the user provides a list combining real actors and real movies together "
        f"(for example: 'Charlize Theron, Blade Runner'), this is completely VALID. Do not flag mixed lists of real "
        f"entities as NOT_FOUND. Instead, accept them and use both elements to guide your suggestions.\n\n"
        f"CREATIVITY DIRECTION: {creativity_instruction}\n\n"
        f"If the input is valid, return exactly 5 high-quality movie recommendations formatted ONLY as a pure HTML <table>. "
        f"DO NOT use markdown pipes (|). DO NOT use code block backticks (```html). Use ONLY English.\n\n"
        f"CRITICAL SYSTEM CONSTRAINTS:\n"
        f"1. EXCLUSION RULE: Never recommend any movie that the user explicitly provided in their input list. "
        f"If they like a movie, exclude it from the results and find new, distinct alternatives.\n"
        f"2. LOGICAL MATCH CODES: Calculate the Match % dynamically based on cinematic similarity to the user's input, "
        f"but keep it relative to the input baseline. Do not list input movies as an 80% match.\n"
        f"3. DATA RELEVANCE: Ensure your suggestions span modern cinema releases up through recent years, matching "
        f"the requested streaming availability context."
    )
    
    payload = {
        "model": "Qwen/Qwen2.5-72B-Instruct",
        "messages": [
            {
                "role": "system", 
                "content": system_content
            },
            {
                "role": "user", 
                "content": f"Validate and process this movie input: {movies}. If valid, provide recommendations for streaming platform: {platform}. Columns: Match %, Title, Year, Synopsis, Stars, Streaming."
            }
        ],
        "temperature": temp_setting,
        "presence_penalty": 0.8,  # Bumped up slightly to punish repetitive recommendations
        "max_tokens": 1200
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        data = response.json()
        output = data['choices'][0]['message']['content'].strip()
        
        if "NOT_FOUND" in output:
            return (
                "<div class='error-msg'>"
                "&ldquo;I'm sorry, Hal, I can't do that. You've listed a film or actor "
                "that I cannot locate. Please try again.&rdquo;"
                "</div>"
            )
            
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
    creativity = "1"  # Default string literal matching slider baseline
    if request.method == 'POST':
        user_input = request.form.get('movie_input', "")
        platform = request.form.get('platform', "").strip()
        if not platform:
            platform = "Any of the above"
            
        # Capture selection as a string to pass cleanly back into HTML value attribute
        creativity = request.form.get('creativity', "1")
        table = query_ai(user_input, platform, creativity)
    return render_template_string(APP_TEMPLATE, table=table, user_input=user_input, creativity=creativity)

# --- UI TEMPLATES ---

LANDING_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Kelly A. Burns | AI Portfolio</title>
    <style>
        @import url('[https://fonts.googleapis.com/css2?family=Inter:wght=200;400;700&display=swap](https://fonts.googleapis.com/css2?family=Inter:wght=200;400;700&display=swap)');
body { 
            margin: 0; 
            background: #05070a; 
            color: white; 
            font-family: 'Inter', sans-serif; 
            display: flex; 
            justify-content: center;
            align-items: flex-start;
            min-height: 100vh; 
            padding: 20px;
            background-image: url('/static/space-ai-bg.jpg');
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }

        .card { 
            background: rgba(10, 15, 25, 0.92); 
            backdrop-filter: blur(20px);
            padding: 30px; 
            border-radius: 28px; 
            width: 92vw;
            max-width: 550px; 
            border: 1px solid rgba(77, 166, 255, 0.3); 
            box-shadow: 0 25px 60px rgba(0,0,0,0.6);
            margin: 20px auto;
            box-sizing: border-box;
        }

        @media (max-width: 480px) {
            h1 { font-size: 2.2rem; }
            p, li { font-size: 1rem !important; }
            .launch-btn { width: 100%; text-align: center; box-sizing: border-box; }
            .card { padding: 20px; }
        }
            
        h1 { font-size: 3rem; font-weight: 200; margin: 0 0 10px 0; letter-spacing: -1px; }
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
        .tech-section { border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 25px; }
        h2 { font-size: 1.2rem; color: #4da6ff; margin-bottom: 15px; font-weight: 700; }
        h3 { font-size: 0.9rem; margin: 20px 0 8px 0; color: rgba(255,255,255,0.9); }
        p { font-size: 0.85rem; line-height: 1.6; color: rgba(255, 255, 255, 0.7); margin-bottom: 15px; }
        .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.05); font-size: 0.75rem; opacity: 0.6; }
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
            <p>I maintained a strict manual audit layer, correcting recursive context-loss issues—such as repeated dropping of environment port configurations and prompt logic—to ensure system stability.</p>
            <h3>Tech Stack</h3>
            <p>Built on a <b>Python/Flask</b> micro-framework. Version control is managed via <b>GitHub</b> with an automated <b>CI/CD pipeline</b> deploying to a cloud-native <b>Railway</b> environment. All UI/UX is proprietary design.</p>
            <h3>The Engine (Qwen 2.5 72B)</h3>
            <p>Utilizes Qwen 2.5 72B via <b>Hugging Face API Router</b> for enterprise-grade reasoning. To manage stochastic randomness and prevent logical hallucinations, I implemented a <b>Temperature Parameter (0.1 - 1.0)</b>, allowing user-level control over prediction probability distributions.</p>
        </div>
        <div class="footer">
            Palm Desert, CA | <a href="mailto:KBurnsDirect@gmail.com" target="_blank" style="color:#4da6ff; text-decoration:none;">KBurnsDirect@gmail.com</a><br>
            LinkedIn: <a href="[https://www.linkedin.com/in/kellyburns-pm](https://www.linkedin.com/in/kellyburns-pm)" target="_blank" style="color:#4da6ff; text-decoration:none;">KellyBurns-PM</a><br>
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
<meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movie Matchmaker</title>
    <style>
        body { margin: 0; background: #05070a; background-image: url('/static/space-ai-bg.jpg'); background-size: cover; background-attachment: fixed; color: white; font-family: 'Inter', sans-serif; display: flex; justify-content: flex-end; align-items: center; min-height: 100vh; padding-right: 5%; }
        .card { background: rgba(10, 15, 25, 0.85); backdrop-filter: blur(25px); padding: 35px; border-radius: 24px; width: 550px; border: 1px solid rgba(77, 166, 255, 0.3); box-shadow: 0 20px 50px rgba(0,0,0,0.6); max-height: 90vh; overflow-y: auto; box-sizing: border-box; }
        .back-link { font-size: 0.85rem; color: #4da6ff; text-decoration: none; opacity: 0.6; display: block; margin-bottom: 10px; }
        h2 { color: #4da6ff; margin: 0; font-weight: 300; font-size: 1.75rem; }
        .subtitle { font-size: 1rem; color: #4da6ff; opacity: 0.7; margin-bottom: 20px; display: block; }
        label { font-size: 1rem; font-weight: bold; opacity: 0.9; display: block; margin-top: 20px; }
        
        .slider-explanation { font-size: 0.85rem; color: rgba(255, 255, 255, 0.8); line-height: 1.5; margin-top: 8px; margin-bottom: 4px; }
        .input-explanation { font-size: 0.85rem; color: rgba(255, 255, 255, 0.8); line-height: 1.5; margin-top: 6px; margin-bottom: 12px; }

        input[type="text"], select { 
            width: 100%; 
            padding: 16px; 
            margin: 10px 0; 
            border-radius: 12px; 
            border: 1px solid rgba(255,255,255,0.15); 
            background: rgba(0,0,0,0.5); 
            color: white; 
            box-sizing: border-box; 
            outline: none; 
            font-size: 16px; 
        }
        
        select option { background: #0a0f19; color: white; }

        input[type="range"] {
            -webkit-appearance: none;
            width: 100%;
            height: 10px;
            border-radius: 5px;
            background: rgba(255,255,255,0.2);
            outline: none;
            margin: 12px 0 6px 0;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #4da6ff;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(77,166,255,0.5);
        }
        input[type="range"]::-moz-range-thumb {
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #4da6ff;
            cursor: pointer;
            box-shadow: 0 0 10px rgba(77,166,255,0.5);
        }

        .btn { background: #4da6ff; color: white; padding: 16px; width: 100%; border: none; border-radius: 50px; font-weight: bold; font-size: 1rem; cursor: pointer; margin-top: 20px; }
        
        #loading { 
            display: none; 
            margin-top: 25px; 
            text-align: center; 
            color: #4da6ff; 
            font-size: 1rem; 
            background: rgba(77, 166, 255, 0.08);
            padding: 18px;
            border-radius: 12px;
            border-left: 3px solid #4da6ff;
            line-height: 1.5;
        }
        .pulse-text { animation: pulse 1.6s infinite ease-in-out; font-weight: bold; display: block; margin-bottom: 4px; }
        @keyframes pulse { 0% { opacity: 0.4; } 50% { opacity: 1; color: #99ccff; } 100% { opacity: 0.4; } }

        .error-msg { margin-top: 25px; background: rgba(255, 77, 77, 0.08); color: #ff4d4d; border-left: 3px solid #ff4d4d; padding: 18px; border-radius: 12px; font-size: 1.05rem; line-height: 1.5; font-style: italic; box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; margin-top: 25px; }
        th { text-align: left; color: #4da6ff; border-bottom: 1px solid rgba(77,166,255,0.2); padding: 10px; font-size: 0.9rem; }
        td { padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.05); vertical-align: top; line-height: 1.4; }
        
        .range-wrap { display: flex; justify-content: space-between; font-size: 0.75rem; color: #4da6ff; opacity: 0.85; font-weight: bold; padding: 0 2px; }
        .range-wrap span { width: 33.33%; }
        .range-wrap .center-label { text-align: center; }
        .range-wrap .right-label { text-align: right; }

        @media (max-width: 600px) {
            body { padding: 10px; justify-content: center; }
            .card { width: 100%; max-height: 95vh; padding: 20px; border-radius: 16px; }
            table { font-size: 0.8rem; }
            td, th { padding: 6px; }
        }
    </style>
</head>
<body>
    <div class="card">
        <a href="/" class="back-link">← Portfolio Home</a>
        <h2>Movie Matchmaker</h2>
        <span class="subtitle">Let's find your next favorite film...</span>
        <form method="POST" action="/app">
            <label>What movies or actors do you love?</label>
            <p class="input-explanation">
                The more movies and/or actors you provide here, the more accurately the AI can map your taste profiles to generate stellar recommendations. Fire away! I'm ready. 😊
            </p>
            <input type="text" name="movie_input" placeholder="e.g. Inception, Heat, Sandra Bullock" value="{{ user_input }}" required>
            
            <label style="margin-top: 20px;">Choose Your Vibe</label>
            <p class="slider-explanation">
                When the slider is at the far left (default mode), you'll see movies that are the <b>most like</b> what you entered. In the middle, you'll get more <b>creative choices</b> with similar actors, directors, or cinematic styles. All the way to the right delivers the <b>most creative choices</b>—out-of-the-box predictions tailored completely to your unique tastes.
            </p>
            <input type="range" name="creativity" min="1" max="10" value="{{ creativity }}">
            <div class="range-wrap">
                <span>Most Likely Choices</span>
                <span class="center-label">Slightly More Creative</span>
                <span class="right-label">Most Creative Choices</span>
            </div>

            <label style="margin-top: 25px;">What's Your Preferred Streaming Service?</label>
            <select name="platform">
                <option value="" selected>Choose a service... (Optional)</option>
                <option value="Netflix">Netflix</option>
                <option value="Amazon Prime">Amazon Prime</option>
                <option value="Hulu">Hulu</option>
                <option value="HBO Max">HBO Max</option>
                <option value="Peacock">Peacock</option>
                <option value="Apple TV+">Apple TV+</option>
                <option value="Any of the above">Any of the above</option>
            </select>
            <button type="submit" class="btn">Find My Matches</button>
        </form>
        
        <div id="loading">
            <span class="pulse-text">Searching the movie universe...</span>
            <span style="opacity:0.85; font-size:0.85rem;">Finding the perfect recommendations for you. This will take about 30 seconds.</span>
        </div>

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
