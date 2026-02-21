from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
        <head><title>Movie AI</title></head>
        <body style="font-family: sans-serif; text-align: center; padding-top: 50px;">
            <h1>🎬 Movie Recommender AI</h1>
            <p>The infrastructure is live! The engine is warming up...</p>
            <p style="color: #666;">Next step: Connecting the AI Brain.</p>
        </body>
    </html>
    """

if __name__ == "__main__":
    # IMPORTANT: Railway assigns a dynamic port. 
    # This code tells Flask to listen on the port Railway provides.
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
