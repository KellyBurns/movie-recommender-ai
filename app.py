# Hugging Face Setup
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {
    "Authorization": f"Bearer {os.environ.get('HF_TOKEN')}",
    "X-Wait-For-Model": "true"  # Force Hugging Face to wait for the model to load
}

def query_ai(movies, platform, creativity):
    temp = float(creativity) / 10.0
    
    # Prompting the model for a strict table output
    prompt = f"[INST] User likes: {movies}. Preferred Platform: {platform}. Provide 10 recommendations. Format as HTML Table: Title, Synopsis, Top 3 Stars, Streaming On. [/INST]"
    
    payload = {
        "inputs": prompt,
        "parameters": {"temperature": temp, "max_new_tokens": 1200}
    }
    
    try:
        # Increased timeout to 90 seconds to give the model time to "thaw"
        response = requests.post(API_URL, headers=headers, json=payload, timeout=90)
        data = response.json()
        
        if isinstance(data, list) and len(data) > 0:
            output = data[0].get('generated_text', "")
            if "<table>" in output:
                return "<table>" + output.split("<table>")[1].split("</table>")[0] + "</table>"
            return "<p>AI results arrived, but weren't in table format. Please try again!</p>"
        return "The AI is still waking up. Please refresh and try one more time."
    except Exception as e:
        return f"Connection error: The AI took too long to wake up. Try again in 10 seconds."

@app.route('/', methods=['GET', 'POST'])
def home():
    table = ""
    if request.method == 'POST':
        user_input = request.form.get('movie_input')
        plat = request.form.get('platform')
        creativity = request.form.get('creativity')
        table = query_ai(user_input, plat, creativity)
    return render_template_string(HTML_TEMPLATE, table=table)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Movie Match Maker AI</title>
    <style>
        body { margin: 0; background: url('/static/space-ai-bg.jpg') no-repeat center center fixed; background-size: cover; color: white; font-family: 'Segoe UI', sans-serif; height: 100vh; display: flex; justify-content: flex-end; align-items: center; padding-right: 5%; }
        .glass-card { background: rgba(0, 0, 0, 0.8); backdrop-filter: blur(15px); padding: 40px; border-radius: 30px; border: 1px solid rgba(255,255,255,0.1); width: 450px; max-height: 90vh; overflow-y: auto; text-align: center; }
        h1 { color: #4da6ff; margin: 0; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: none; background: rgba(255,255,255,0.1); color: white; box-sizing: border-box; }
        .btn { background: #4da6ff; color: white; padding: 15px; width: 100%; border: none; border-radius: 50px; font-weight: bold; cursor: pointer; margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 0.8rem; background: rgba(0,0,0,0.3); }
        th, td { border: 1px solid rgba(255,255,255,0.1); padding: 8px; text-align: left; }
    </style>
</head>
<body>
    <div class="glass-card">
        <h1>Movie Match Maker AI</h1>
        <p>Explorations in AI Development</p>
        <form method="POST" id="movieForm">
            <input type="text" name="movie_input" placeholder="Movies you love..." required>
            <select name="platform">
                <option value="Anywhere">Anywhere</option>
                <option value="Netflix">Netflix</option>
                <option value="Amazon Prime">Amazon Prime</option>
                <option value="HBO Max">HBO Max</option>
                <option value="Disney+">Disney+</option>
                <option value="Hulu">Hulu</option>
                <option value="Apple TV+">Apple TV+</option>
            </select>
            <label>Creativity (1 Accurate - 10 Creative)</label>
            <input type="range" name="creativity" min="1" max="10" value="5">
            <button type="submit" class="btn" id="submitBtn">Find My Matches</button>
        </form>
        <div id="results">
            {% if table %}{{ table|safe }}{% endif %}
        </div>
    </div>
    <script>
        const form = document.getElementById('movieForm');
        const btn = document.getElementById('submitBtn');
        form.onsubmit = () => {
            btn.innerHTML = "Waking up the AI... Please wait.";
            btn.disabled = true;
            btn.style.opacity = "0.5";
        };
    </script>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
