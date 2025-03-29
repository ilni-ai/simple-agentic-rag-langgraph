from flask import Flask
from flask_cors import CORS
from rag_routes import rag_api

app = Flask(__name__)
CORS(app)  # ✅ Allow CORS for all origins — safe for local dev

app.register_blueprint(rag_api)

if __name__ == "__main__":
    app.run(debug=True)
