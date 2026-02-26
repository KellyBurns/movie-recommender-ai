import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

# The most stable 2026 Router endpoint
API_URL = "https://router.huggingface.co/hf-inference/v1/chat/completions"
HF_TOKEN = os.environ.get('HF_TOKEN')

def query_ai(movies, platform, creativity):
    if not HF_TOKEN:
        return "<p style='color:red;'>Error: HF_TOKEN missing in Railway!</p>"
    
    headers = {
        "Authorization": f"Bearer {HF_TOKEN.strip()}",
        "Content-Type": "application/json"
    }
    
    # We'll try the Nemo model - highly stable in 2026
    payload = {
        "model": "mistralai/Mistral-Nemo-Instruct-2407",
        "messages": [
            {"role": "system", "content": "Return ONLY an HTML table. No text."},
            {"role": "user", "content": f"Recommend 10 movies for fans of {movies} on {platform}."}
        ],
        "temperature": float(creativity) / 10.0,
        "max_tokens": 800
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 404:
            return f"<div style='color:orange;'><b>Router Error 404:</b> Model not found. <br><small>Try changing the 'model' string in app.py to 'meta-llama/Llama-3.2-3B-Instruct'</small></div>"
            
        if response.status_code != 200:
            return f"<div style='color:orange;'><b>AI Error {response.status_code}:</b> {response.text}</div>"
            
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
    <title>Movie AI</title>
    <style>
        body { margin: 0; background: #0b0d17; background-image: url('/static/space-ai-bg.jpg'); background-size: cover; color: white; font-family: sans-serif; height: 100vh; display: flex; justify-content: flex-end; align-items: center; padding-right: 5%; }
        .card { background: rgba(0,0,0,0.8); padding: 30px; border-radius: 20px; width: 400px; border: 1px solid #4da6ff; }
        input, select { width: 100%; padding: 10px; margin: 10px 0; border-radius: 5px; border: 1px solid #4da6ff; background: #111; color: white; }
        .btn { background: #4da6ff; color: white; padding: 12px; width: 100%; border: none; border-radius: 20px; cursor: pointer; font-weight: bold; }
        .results { margin-top: 20px; font-size: 0.8rem; max-height: 300px; overflow: auto; }
        table { width: 100%; border-collapse: collapse; }
        td, th { border: 1px solid #333; padding: 5px; }
    </style>
</head>
<body>
    <div class="card">
        <h2>Movie Match Maker</h2>
        <form method="POST">
            <input type="text" name="movie_input" placeholder="Movies you like..." value="{{ user_input }}" required>
            <select name="platform"><option>Anywhere</option><option>Netflix</option></select>
            <input type="range" name="creativity" min="1" max="10" value="5">
            <button type="submit" class="btn">Find My Matches</button>
        </form>
        {% if table %}<div class="results">{{ table|safe }}</div>{% endif %}
    </div>
</body>
</html>
"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
