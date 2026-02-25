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
                /* Updated to match your specific filename */
                background: url('/static/space-ai-bg.jpg') no-repeat center center fixed; 
                background-size: cover;
                color: white;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-shadow: 2px 2px 8px rgba(0,0,0,0.8);
            }
            .glass-card {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                -webkit-backdrop-filter: blur(10px);
                padding: 40px;
                border-radius: 20px;
                border: 1px solid rgba(255,255,255,0.2);
                text-align: center;
                max-width: 80%;
            }
            h1 { font-size: 3rem; margin: 0; }
            p { font-size: 1.5rem; opacity: 0.9; margin-top: 10px; }
            .btn {
                margin-top: 25px;
                display: inline-block;
                padding: 12px 30px;
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
    return "<h1>Movie Brain Loading...</h1><p>We'll connect the Hugging Face logic tomorrow!</p>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
