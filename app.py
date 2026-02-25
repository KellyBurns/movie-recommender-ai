import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Kelly A. Burns | AI Portfolio</title>
        <style>
            body {
                margin: 0;
                padding: 0;
                background: url('/static/space-ai-bg.jpg') no-repeat center center fixed; 
                background-size: cover;
                color: white;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                height: 100vh;
                display: flex;
                /* This moves the content to the right side */
                justify-content: flex-end; 
                align-items: center;
                /* This keeps the card from touching the actual edge */
                padding-right: 10%; 
            }
            .glass-card {
                background: rgba(0, 0, 0, 0.6);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                padding: 50px;
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.2);
                text-align: center;
                max-width: 400px;
                box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
            }
            h1 { font-size: 2.8rem; margin: 0; line-height: 1.1; }
            p { font-size: 1.3rem; margin-top: 15px; opacity: 0.9; }
            .btn {
                margin-top: 30px;
                display: inline-block;
                padding: 12px 35px;
                background: #4da6ff;
                color: white;
                text-decoration: none;
                border-radius: 50px;
                font-weight: bold;
                transition: 0.3s;
            }
            .btn:hover { background: #007bff; transform: scale(1.05); }
        </style>
    </head>
    <body>
        <div class="glass-card">
            <h1>Kelly A. Burns</h1>
            <p>Explorations in AI development</p>
            <a href="/movies" class="btn">Launch Movie Recommender</a>
        </div>
    </body>
    </html>
    """

@app.route('/movies')
def movies():
    return "<h1>Movie Brain Loading...</h1><p>See you tomorrow!</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
