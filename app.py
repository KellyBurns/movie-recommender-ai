import os
import random
from flask import Flask

app = Flask(__name__)

# A "spellbinding" list for someone who loves Sharp Objects
thrillers = [
    {"title": "Gone Girl", "desc": "A dark look at a marriage gone wrong when a wife disappears."},
    {"title": "The Girl on the Train", "desc": "An alcoholic voyeur becomes entangled in a missing persons investigation."},
    {"title": "The Killing (TV Series)", "desc": "Atmospheric, rain-soaked, and deeply addictive mystery."},
    {"title": "Wind River", "desc": "A chilling mystery set on a remote Wyoming reservation."},
    {"title": "The Night Of", "desc": "A gripping, high-tension dive into a complex murder case."}
]

@app.route('/')
def home():
    selection = random.choice(thrillers)
    return f"""
    <html>
        <head>
            <title>Spellbinding Recommendations</title>
            <style>
                body {{ font-family: 'Georgia', serif; background-color: #0f0f0f; color: #e0e0e0; text-align: center; padding: 50px; }}
                .container {{ border: 1px solid #333; padding: 40px; border-radius: 8px; display: inline-block; max-width: 600px; background: #1a1a1a; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
                h1 {{ color: #b12704; letter-spacing: 2px; }}
                .movie-title {{ font-size: 2em; color: #fff; margin: 20px 0; font-style: italic; }}
                .desc {{ font-size: 1.1em; color: #aaa; line-height: 1.6; }}
                .btn {{ display: inline-block; margin-top: 30px; padding: 10px 20px; background: #b12704; color: white; text-decoration: none; border-radius: 4px; }}
                .btn:hover {{ background: #ff3300; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎬 THE DARK ROOM</h1>
                <p>Because you need something that grips you...</p>
                <div class="movie-title">{selection['title']}</div>
                <p class="desc">{selection['desc']}</p>
                <a href="/" class="btn">GIVE ME ANOTHER</a>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
