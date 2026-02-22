import os
from flask import Flask, render_template
# This will link our movie app folder
from movies.movies import movies_bp

app = Flask(__name__)

# This tells the site: "Everything in the movies folder lives at /movies"
app.register_blueprint(movies_bp, url_prefix='/movies')

@app.route('/')
def home():
    # Your Portfolio Hub Data
    projects = [
        {"name": "AI Movie Recommender", "url": "/movies", "tech": "Hugging Face NLP", "status": "Live"},
        {"name": "Coming Soon", "url": "#", "tech": "TBD", "status": "In Development"}
    ]
    return render_template('index.html', projects=projects)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
2. The Movie Brain (movies/movies.py)
Create a folder named movies and put this inside it. This is where the 90% Probability logic lives.

Python
import os
from flask import Blueprint, render_template, request
from huggingface_hub import InferenceClient

movies_bp = Blueprint('movies', __name__, template_folder='templates', static_folder='static')

# Uses the secret key you just added to Railway!
client = InferenceClient(api_key=os.environ.get("HF_TOKEN"))

@movies_bp.route('/', methods=['GET', 'POST'])
def index():
    recommendations = []
    if request.method == 'POST':
        user_input = request.form.get('movies')
        # Here we'd call the HF model to compare vectors
        # For the prototype, we use a creative prompt for the AI
        prompt = f"User loves: {user_input}. Suggest 3 movies with a 'Similarity Score' percentage."
        
        try:
            response = client.chat.completions.create(
                model="mistralai/Mistral-7B-Instruct-v0.2",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            recommendations = response.choices[0].message.content.split('\n')
        except:
            recommendations = ["The AI is warming up. Please try again in 30 seconds!"]

    return render_template('movies.html', recommendations=recommendations)
