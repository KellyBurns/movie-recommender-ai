import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# The specific 2026 base URL for the chat router
API_URL = "https://router.huggingface.co/v1/chat/completions"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity):
    if not HF_TOKEN:
        return "<p style='color:red;'>Error: HF_TOKEN missing in Railway!</p>"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN.strip()}",
        "Content-Type": "application/json"
    }
    
    # Adding ':fastest' tells the router to pick ANY available provider automatically
    payload = {
        "model": "meta-llama/Llama-3.2-3B-Instruct:fastest",
        "messages": [
            {"role": "system", "content": "You are a movie expert. Return ONLY an HTML table."},
            {"role": "user", "content": f"Recommend 10 movies for fans of {movies} on {platform}. Table columns: Title, Synopsis, Stars, Streaming."}
        ],
        "temperature": float(creativity) / 10.0,
        "max_tokens": 1000
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        
        if response.status_code != 200:
            return f"<div style='color:orange;'><b>Router Error {response.status_code}:</b> {response.text}</div>"
            
        data = response.json()
        output = data['choices'][0]['message']['content']
        
        if "<table>" in output:
            return "<table>" + output.split("<table>")[1].split("</table>")[0] + "</table>"
        return f"<div class='results-area'>{output}</div>"

    except Exception as e:
        return f"<p>Technical Error: {str(e)}</p>"

@app.route('/', methods=['GET', 'POST'])
def home():
    table = ""
    user_input = ""
    if request.method == 'POST':
        user_input = request.form.get('movie_input', "")
        table = query_ai(user_input, request.form.get('platform', "Anywhere"), request.form.get('creativity', "5"))
    
    return render_template_string(HTML_TEMPLATE, table=table, user_input=user_input)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Movie AI Recommender</title>
    <style>
        body { margin: 0; background: #0b0d17; background-image: url('/static/space-ai-bg.jpg'); background-size: cover; background-attachment: fixed; color: white; font-family: sans-serif; height: 100vh; display: flex; justify-content: flex-end; align-items: center; padding-right: 5%; }
        .card { background: rgba(0,0,0,0.85); backdrop-filter: blur(10px); padding: 30px; border-radius: 20px; width: 420px; border: 1px solid #4da6ff; max-height: 90vh; overflow-y: auto; }
        input, select { width: 100%; padding: 12px; margin: 10px 0; border-radius: 8px; border: 1px solid #4da6ff; background: #111; color: white; box-sizing: border-box; }
        .btn { background: #4da6ff; color: white; padding: 15px; width: 100%; border: none; border-radius: 30px; cursor: pointer; font-weight: bold; margin-top: 10px; }
        .results { margin-top: 25px; font-size: 0.85rem; border-top: 1px solid #4da6ff; padding-top: 15px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        td, th { border: 1px solid #333; padding: 8px; text-align: left; }
        th { color: #4da6ff; }
    </style>
</head>
<body>
    <div class="card">
        <h2 style="color:#4da6ff; margin-top:0;">Movie Match Maker</h2>
        <form method="POST">
            <input type="text" name="movie_input" placeholder="Enter movies you like..." value="{{ user_input }}" required>
            <select name="platform"><option>Anywhere</option><option>Netflix</option><option>Amazon Prime</option><option>Disney+</option></select>
            <label style="font-size: 0.8rem;">Creativity Level</label>
            <input type="range" name="creativity" min="1" max="10" value="7">
            <button type="submit" class="btn">Find Movies</button>
        </form>
        {% if table %}<div class="results">{{ table|safe }}</div>{% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
