import os
from flask import Flask, render_template

# Initialize the main website
app = Flask(__name__)

# HOMEPAGE ROUTE
@app.route('/')
def home():
    # This is where your Space-themed portfolio hub will live
    projects = [
        {"name": "AI Movie Recommender", "url": "/movies", "tech": "Hugging Face NLP", "status": "Coming Soon"},
        {"name": "Future AI Exploration", "url": "#", "tech": "TBD", "status": "In Development"}
    ]
    return render_template('index.html', projects=projects)

# MOVIE APP ROUTE (Placeholder for now)
@app.route('/movies')
def movies():
    return "<h1>Movie Brain Loading...</h1><p>We will connect the Hugging Face logic here tomorrow!</p>"

# RAILWAY PORT BINDING (Must be at the very bottom)
if __name__ == "__main__":
    # Railway provides a dynamic port; this line grabs it
    port = int(os.environ.get("PORT", 8080))
    # '0.0.0.0' makes the site accessible to the public web
    app.run(host='0.0.0.0', port=port)
