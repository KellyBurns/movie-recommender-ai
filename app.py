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

    # UPDATED VALIDATION RULE: Explicitly permits musical icons/crossover artists to prevent false-positive NOT_FOUND flags
    system_content = (
        f"You are an expert movie database API and recommendation engine. "
        f"Your first job is to validate the user's input. If the input consists of completely made-up gibberish, "
        f"random keyboard typing, or entirely fictional titles/people that do not exist in reality, you MUST "
        f"return exactly the word: NOT_FOUND. Do not return anything else.\n\n"
        f"CRITICAL VALIDATION RULE: If the user provides real actors, real directors, or iconic musical crossover artists "
        f"who have starred in or contributed heavily to cinema (for example: 'Michael Jackson', 'David Bowie', or 'Charlize Theron, Blade Runner'), "
        f"this is completely VALID. Do not flag real people or real musical entities as NOT_FOUND. Instead, accept them "
        f"and provide creative cinematic suggestions based on their filmography, musical films, documentaries, or visual style.\n\n"
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
        "presence_penalty": 0.8,
        "max_tokens": 1200
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=120)
        data = response.json()
        output = data['choices'][0]['message']['content'].strip()
        
        if "NOT_FOUND" in output:
            return (
                "<div class='error-msg'>"
                "&ldquo;I'm sorry, Dave. I'm afraid I can't do that. You've listed a film or actor "
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
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        * { box-sizing: border-box; }

        body {
            margin: 0;
            background: #05070a url('/static/hero-network.jpg') top center / 100% auto no-repeat;
            color: white;
            font-family: 'Inter', sans-serif;
            display: flex;
            justify-content: center;
        }

        .page {
            width: 100%;
            max-width: 1600px;
            padding: 90px 40px 40px;
        }

        .site-header {
            text-align: center;
            margin-bottom: 56px;
        }

        .site-header h1 {
            margin: 0;
            font-size: 3.75rem;
            font-weight: 800;
            letter-spacing: -0.01em;
        }

        .subtitle {
            margin: 10px 0 0;
            font-size: 1.15rem;
            font-weight: 400;
            color: #b9c2cc;
        }

        .cards {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 32px;
            max-width: 1420px;
            margin: 0 auto;
        }

        .card {
            background: rgba(10, 18, 34, 0.55);
            border: 1px solid rgba(77, 166, 255, 0.28);
            border-radius: 14px;
            padding: 36px 36px 32px;
            backdrop-filter: blur(6px);
            display: flex;
            flex-direction: column;
        }

        .card-title {
            margin: 0 0 18px;
            font-size: 1.75rem;
            font-weight: 700;
            color: #4da6ff;
        }

        .card h3 {
            margin: 18px 0 6px;
            font-size: 1.05rem;
            font-weight: 600;
            color: white;
        }

        .card h3:first-of-type { margin-top: 0; }

        .card p {
            margin: 0;
            font-size: 0.95rem;
            line-height: 1.6;
            color: #b9c2cc;
        }

        .card-divider {
            border: none;
            border-top: 1px solid rgba(255, 255, 255, 0.12);
            margin: 24px 0 20px;
        }

        .launch-btn {
            align-self: flex-start;
            display: inline-block;
            padding: 11px 34px;
            border-radius: 999px;
            background: linear-gradient(135deg, #3b8cff, #1a5fd1);
            color: white;
            font-weight: 600;
            font-size: 0.95rem;
            text-decoration: none;
            transition: transform 0.2s;
        }
        .launch-btn:hover { transform: scale(1.05); }

        .footer {
            max-width: 1420px;
            margin: 48px auto 0;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.05);
            text-align: center;
            font-size: 0.75rem;
            opacity: 0.6;
        }
        .footer p { margin: 4px 0; }
        .footer a { color: #4da6ff; text-decoration: none; }

        @media (max-width: 900px) {
            .cards { grid-template-columns: 1fr; }
            .site-header h1 { font-size: 2.5rem; }
            .page { padding: 60px 20px 30px; }
        }
    </style>
</head>
<body>
    <div class="page">

        <header class="site-header">
            <h1>Kelly A. Burns</h1>
            <p class="subtitle">Explorations in AI Development</p>
        </header>

        <main class="cards">

            <section class="card">
                <h2 class="card-title">Agentic AI</h2>

                <h3>What It Is</h3>
                <p>"Healthcare Feature Review Board" is an Agentic AI-powered tool for Product Managers in Healthcare simulating a cross-functional product review. Just submit a healthcare feature idea, and four specialist agents&mdash;product, clinical workflow, patient experience, and risk/security&mdash;evaluate it for you in parallel, then a synthesis agent reconciles their findings into one recommendation.</p>

                <h3>Human-In-The-Loop Collaboration</h3>
                <p>I architected this multi-agent system using Claude Code as the engineering partner, working one phase at a time against a 16-phase build plan. Total build time from idea to final polish: 20 hours, solo. I maintained a strict manual audit at every checkpoint&mdash;reviewing agent outputs, catching malformed-JSON failures, verifying provider failback&mdash;before any commit reached main.</p>

                <h3>Tech Stack</h3>
                <p>Python/Flask, orchestrated with LangGraph. GitHub version control with automated CI/CD to Railway. The workflow graph renders live via Mermaid; results stream over Server-Sent Events (SSE). UI/UX is my proprietary design.</p>

                <h3>The Engine (Qwen3-235B-A22B)</h3>
                <p>Qwen3-235B-A22B-Instruct-2507, a non-thinking Mixture-of-Experts (MoE) model, served via the Hugging Face Inference Providers router with ":cheapest" routing across multiple providers for automatic failback. Four specialist agents run in parallel, each returning strict, schema-validated JSON; a synthesis agent reconciles their output. Malformed calls get one automatic retry; per-agent token caps bound cost and latency.</p>

                <h3>Why This Model</h3>
                <p>Its MoE architecture delivers large-model reasoning at a fraction of the inference cost, it's ungated with no licensing friction, and it's served by multiple providers&mdash;which made the ":cheapest" failback routing possible.</p>

                <hr class="card-divider">
                <a href="https://healthcare-feature-review-board-production.up.railway.app/" target="_blank" rel="noopener noreferrer" class="launch-btn">Launch Project</a>
            </section>

            <section class="card">
                <h2 class="card-title">Generative AI</h2>

                <h3>What It Is</h3>
                <p>"Movie Matchmaker" is an AI-powered cinematic recommendation engine designed for anyone who loves movies. Simply input your favorite movies, actors, or directors&mdash;and choose your desired vibe and streaming platform&mdash;and the system validates your input, analyzes cinematic themes, and dynamically generates tailored recommendations complete with match percentages, synopses, cast details, and streaming availability.</p>

                <h3>Human-In-The-Loop Collaboration</h3>
                <p>I architected this solo project through an AI-augmented prototyping process, employing Gemini 3 Flash to accelerate full-stack logic bridging back-end micro-infrastructure with front-end user experience. I maintained a strict manual audit layer throughout&mdash;correcting recursive context-loss issues, environment configuration drops, and prompt validation gates&mdash;to guarantee real-world edge-case stability.</p>

                <h3>Tech Stack</h3>
                <p>Python/Flask micro-framework. Version control managed via GitHub with an automated CI/CD pipeline deploying to a cloud-native Railway environment. All UI/UX features are my proprietary responsive glassmorphism design.</p>

                <h3>The Engine (Qwen 2.5 72B)</h3>
                <p>Utilizes Qwen 2.5 72B via the Hugging Face API Router for enterprise-grade reasoning. To control generation variance and mitigate hallucinations, I mapped a user-controlled sampling Temperature Parameter (0.1 - 1.0) tied to dynamic prompt strategies, dynamically shifting system directions from strict, deterministic baseline matches to high-creativity indie predictions.</p>

                <h3>Why This Model</h3>
                <p>Qwen 2.5 72B provides massive world-knowledge coverage across global film datasets, exceptionally strong adherence to complex system prompts, and native ability to reliably output clean HTML structures without backtick artifacts or formatting failures.</p>

                <hr class="card-divider">
                <a href="/app" class="launch-btn">Launch Project</a>
            </section>

        </main>

        <footer class="footer">
            <p>&copy; 2026&ndash;2027 Kelly A. Burns. All Rights Reserved. Verified Projects.</p>
            <p>Palm Desert, CA&nbsp;&nbsp;|&nbsp;&nbsp;E: <a href="mailto:KBurnsDirect@gmail.com">KBurnsDirect@gmail.com</a>&nbsp;&nbsp;|&nbsp;&nbsp;LinkedIn: <a href="https://www.linkedin.com/in/kellyburns-pm/" target="_blank" rel="noopener noreferrer">KellyBurns-PM</a></p>
        </footer>

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
            <span style="opacity:0.85; font-size:0.85rem;">Finding the perfect recommendations for you. The first run can take up to 90 seconds while the model warms up. Repeat runs are faster.</span>
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
