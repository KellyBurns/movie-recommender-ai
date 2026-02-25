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
                justify-content: flex-end; 
                align-items: center;
                padding-right: 8%; 
            }
            .glass-card {
                background: rgba(0, 0, 0, 0.65);
                backdrop-filter: blur(15px);
                -webkit-backdrop-filter: blur(15px);
                
                /* TALLER LOOK: High top/bottom padding, tighter side padding */
                padding: 80px 40px; 
                
                border-radius: 30px;
                border: 1px solid rgba(255,255,255,0.15);
                text-align: center;
                
                /* NO-WRAP PROTECTION: ensures your name stays on one line */
                min-width: 320px; 
                display: flex;
                flex-direction: column;
                justify-content: center;
                box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            }
            h1 { 
                font-size: 2.5rem; 
                margin: 0; 
                white-space: nowrap; /* Forces name to stay on one line */
            }
            p { 
                font-size: 1.2rem; 
                margin-top: 30px; 
                opacity: 0.8; 
                line-height: 1.4;
            }
            .btn {
                margin-top: 50px; /* Pushes button further down for verticality */
                display: inline-block;
                padding: 15px 30px;
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
            <p>Explorations in<br>AI development</p>
            <a href="/movies" class="btn">Launch Project</a>
        </div>
    </body>
    </html>
    """

@app.route('/movies')
def movies():
    return "<h1>Movie Brain Loading...</h1>"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
