from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Agent is Running..."

if __name__ == "__main__":      # Get port from environment or default to 10000 (Render default)
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
