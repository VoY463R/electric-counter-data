from flask import Flask, render_template
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
Bootstrap5(app)

@app.route('/')
def home():
    return "Hello"

if __name__ == "__main__":
    app.run(debug=True)