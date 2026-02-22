import os
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    # This will now successfully find templates/index.html
    return render_template('index.html')

@app.route('/movies')
def movies():
    return "<h1>Movie Brain Loading...</h1><p>We will add the HF logic here tomorrow!</p>"

if __name__ == "__main__":
    # The 'Handshake' Railway needs
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
