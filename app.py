import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# Hugging Face Setup
# Using Mistral-7B-Instruct for high-quality reasoning and fact retrieval
API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
headers = {"Authorization": f"Bearer {os.environ.get('HF_TOKEN')}"}

def query_ai(movies, platform, creativity):
    # Mapping 1-10 slider to 0.1-1.0 temperature range
    temp = float(creativity) / 10.0
    
    # The prompt engineered for a structured HTML table output
    prompt = f"""
    User likes these movies: {movies}. 
    Preferred Streaming Platform: {platform}.
    Provide 10 movie recommendations that match this vibe. 
    Format the output ONLY as an HTML table with these exact columns: 
    Title, Synopsis, Top 3 Stars, and Streaming On.
    If 'Anywhere' is selected, suggest movies from any major service.
    Do not include any introductory or concluding text.
    """
    
    payload = {
        "inputs": f"<s>[INST] {prompt} [/INST]",
        "parameters": {
            "temperature": temp, 
            "max_new_tokens": 1200,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload)
        output = response.json()[0]['generated_text']
        
        # Simple extraction to ensure we only display the table
        if "<table>" in output:
            return output.split("<table>")[1].split("</table>")[0]
        return output
    except Exception as e:
        return "The AI is currently warming up or busy. Please wait 30 seconds and try again!"

@app.route('/', methods=['GET', 'POST'])
def home():
    recommendation_table = ""
    if request.method == 'POST':
        user_movies = request.form.get('movie_input')
        platform = request.form.get('platform')
        creativity = request.form.get('creativity')
        recommendation_table = query_ai(user_movies, platform, creativity)

    return render_template_string(HTML_TEMPLATE, table=recommendation_table)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Movie Match Maker | AI Portfolio</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: url('/static/space-ai-bg.jpg') no-repeat center center fixed; 
            background-size: cover;
            color: white;
            font-family: 'Segoe UI', Tahoma, sans-serif;
            height: 100vh;
            display: flex;
            justify-content: flex-end; /* Moves card to the right */
            align-items: center;
            padding-right: 8%; /* Margin from the right edge */
        }
        .glass-card {
            background: rgba(0, 0, 0, 0.75);
            backdrop-filter: blur(15px);
            -webkit-backdrop-filter: blur(15px);
            padding: 50px 40px;
            border-radius: 30px;
            border: 1px solid rgba(255,255,255,0.15);
            text-align: center;
            width: 480px;
            max-height: 85vh;
            overflow-y: auto;
            box-shadow: 0 10px 40px rgba(0,0,0,0.6);
        }
        h1 { 
            font-size: 2.4rem; 
            margin: 0; 
            white-space: nowrap; /* Prevents name wrapping */
            color: #4da6ff;
        }
        .subheader { 
            font-size: 1rem; 
            opacity: 0.7; 
            margin-bottom: 30px;
            letter-spacing: 1px;
        }
        input[type="text"], select {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border-radius: 8px;
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.1);
            color: white;
            box-sizing: border-box;
        }
        label { display: block; margin-top: 15px; font-size: 0.9rem; opacity: 0.9; }
        input[type="range"] { width: 100%; margin: 10px 0; cursor: pointer; }
        .btn {
            background: #4da6ff;
            color: white;
            padding: 15px;
            width: 100%;
            border: none;
            border-radius: 50px;
            font-weight: bold;
            font-size: 1rem;
            cursor: pointer;
            transition: 0.3s;
            margin-top: 20px;
        }
        .btn:hover { background: #007bff; transform: scale(1.02); }
        
        /* Table Styling */
        .results-container { margin-top: 30px; text-align: left; }
        table { width: 100%; border-collapse: collapse; font-size: 0.85rem; }
        th, td { border: 1px solid rgba(255,255,255,0.1); padding: 10px; vertical-align: top; }
        th { background: rgba(77, 166, 255, 0.2); color: #4da6ff; }
    </style>
</head>
<body>
    <div class="glass-card">
        <h1>Movie Match Maker AI</h1>
        <div class="subheader">Explorations in AI Development</div>
        
        <form method="POST">
            <input type="text" name="movie_input" placeholder="Enter movies you love..." required>
            
            <label>Select Streaming Service</label>
            <select name="platform">
                <option value="Anywhere">Anywhere</option>
                <option value="Netflix">Netflix</option>
                <option value="Amazon Prime">Amazon Prime</option>
                <option value="HBO Max">HBO Max</option>
                <option value="Disney+">Disney+</option>
                <option value="Hulu">Hulu</option>
            </select>
            
            <label>Creativity Level (1 = Accurate, 10 = Surprising)</label>
            <input type="range" name="creativity" min="1" max="10" value="5">
            
            <button type="submit" class="btn">Find My Matches</button>
        </form>

        {% if table %}
        <div class="results-container">
            <h3>Your Top 10 Picks</h3>
            <table>
                {{ table|safe }}
            </table>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
