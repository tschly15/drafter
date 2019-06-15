from flask import Flask

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return "<html><title>Inside Draft App</title><h1>Draft App</h1><p>Welcome</p></html>"

app.run()
