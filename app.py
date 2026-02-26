import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# 2026 Stable Router Path
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity):
    if not HF_TOKEN:
        return "<p style='color:red;'>Error: HF_TOKEN missing!</p>"
    
    headers = {"Authorization": f"Bearer {HF_TOKEN.strip()}", "Content-Type": "application/json"}
    temp = min(float(creativity) / 10.0, 0.9)
    
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct:fastest",
        "messages": [
            {
                "role": "system", 
                "content": "You are a precise movie database API. Return ONLY a valid HTML table. NO MARKDOWN. NO CONVERSATION. ORDER: Match %, Title, Year, Synopsis, Stars, Streaming. Ensure Synopsis is in English only."
            },
            {
                "role": "user", 
                "content": f"Recommend 10 movies for a fan of {movies} on {platform}. Format: <table> tags only."
            }
        ],
        "temperature": temp,
        "presence_penalty": 0.5,
        "max_tokens": 1400
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        if response.status_code != 200:
            return f"<div style='color:orange;'>AI is recalibrating. Try one more time!</div>"
            
        data = response.json()
        output = data['choices'][0]['message']['content']
        
        if "<table>" in output:
            table_html = output.split("<table>")[1].split("<table>")[0]
            return '<table id="movieTable">' + table_html + '</table>'
        
        return "<div class='ai-text-fallback'>The AI had a glitch. Please refresh and try again.</div>"
    except Exception as e:
        return f"<p>Error: {str(e)}</p>"

@app.route('/', methods=['GET', 'POST'])
def home():
    table = ""
    user_input = ""
    if request.method == 'POST':
        user_input = request.form.get('movie_input', "")
        table = query_ai(user_input, request.form.get('platform', "Anywhere"), request.form.get('creativity', "7"))
    
    return render_template_string(HTML_TEMPLATE, table=table, user_input=user_input)

HTML_TEMPLATE = """
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
        h2 { color: #4da6ff; margin-bottom: 0px; font-weight: 300; letter-spacing: 1px; }
        .subtitle { font-size: 0.9rem; color: #4da6ff; opacity: 0.7; margin-bottom: 25px; display: block; }
        label { font-size: 0.8rem; opacity: 0.8; display: block; margin-top: 15px; }
        
        /* Pro Tip Styling */
        .hint { 
            font-size: 0.75rem; color: #4da6ff; opacity: 0.9; 
            margin-top: 10px; display: block; line-height: 1.4; 
            border-left: 2px solid #4da6ff; padding-left: 10px;
        }

        input, select { 
            width: 100%; padding: 14px; margin: 8px 0; border-radius: 12px; 
            border: 1px solid rgba(255,255,255,0.1); background: rgba(0,0,0,0.4); 
            color: white; font-size: 1rem; box-sizing: border-box; outline: none; transition: 0.3s;
        }
        input:focus { border-color: #4da6ff; box-shadow: 0 0 10px rgba(77,166,255,0.3); }
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
        .sort-info { font-size: 0.75rem; color: #4da6ff; margin-bottom: 10px; font-style: italic; }
        table { width: 100%; border-collapse: collapse; font-size: 0.8rem; table-layout: fixed; }
        th { text-align: left; color: #4da6ff; padding: 10px 5px; border-bottom: 1px solid rgba(77, 166, 255, 0.2); }
        th:nth-child(1), th:nth-child(3) { cursor: pointer; text-decoration: underline; width: 65px; }
        th:nth-child(2) { width: 110px; }
        th:hover { color: #fff; }
        td { padding: 10px 5px; border-bottom: 1px solid rgba(255,255,255,0.05); color: #ddd; vertical-align: top; overflow: hidden; }
        td:first-child { font-weight: bold; color: #4da6ff; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Movie Match Maker [BETA]</h2>
        <span class="subtitle">Let's find your next favorite film...</span>
        <form method="POST" id="movieForm">
            <label>What movies or actors do you love? (separate with commas)</label>
            <input type="text" name="movie_input" placeholder="e.g. Inception, Heat, Sandra Bullock" value="{{ user_input }}" required>
            <span class="hint"><b>Pro Tip:</b> The more films and/or actors you provide, the better the AI can triangulate your specific taste in pacing, cinematography, and themes.</span>
            
            <label style="margin-top: 20px;">Where are you watching?</label>
            <select name="platform">
                <option selected disabled>Select Streaming Service</option>
                <option value="Anywhere">Anywhere</option>
                <option value="Netflix">Netflix</option>
                <option value="Amazon Prime">Amazon Prime</option>
                <option value="HBO Max">HBO Max</option>
                <option value="Disney+">Disney+</option>
            </select>
            
            <label>Creativity Level</label>
            <input type="range" name="creativity" min="1" max="10" value="7">
            <div class="range-labels">
                <span>1: Predictable Hits</span>
                <span>10: Deep Cuts</span>
            </div>
            <button type="submit" class="btn" id="submitBtn">Find My Matches</button>
        </form>
        <div id="loading-state">
            <div class="spinner"></div>
            <span style="margin-left: 10px; font-size: 0.9rem; color: #4da6ff;">Consulting the Multiverse...</span>
        </div>
        {% if table %}
        <div class="results">
            <div class="sort-info">Sort: Match % or Year (Click headers)</div>
            <div id="resultsTable">{{ table|safe }}</div>
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
        document.addEventListener('click', function (e) {
            if (!e.target.matches('#movieTable th')) return;
            const table = e.target.closest('table');
            const tbody = table.querySelector('tbody') || table;
            const rows = Array.from(tbody.querySelectorAll('tr')).filter(tr => tr.querySelector('td'));
            const headerIndex = Array.from(e.target.parentNode.children).indexOf(e.target);
            if (headerIndex !== 0 && headerIndex !== 2) return;
            const isAscending = e.target.classList.contains('th-sort-asc');
            rows.sort((a, b) => {
                const aVal = parseInt(a.children[headerIndex].textContent.replace(/\D/g,'')) || 0;
                const bVal = parseInt(b.children[headerIndex].textContent.replace(/\D/g,'')) || 0;
                return isAscending ? (aVal - bVal) : (bVal - aVal);
            });
            rows.forEach(row => tbody.appendChild(row));
            e.target.classList.toggle('th-sort-asc', !isAscending);
        });
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
