from flask import Flask

app = Flask('parable')

@app.route('/')
def index():
    return "<p>Hello World</p>"