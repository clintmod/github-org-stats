from flask import Flask
import stats
import logging
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)

@app.route('/')
def index():
    return "Github stats api. Invoke with /[github org]"

@app.route('/<string:org>')
def flatten_stats(org):
    response = app.response_class(
        response=stats.flatten_stats(org),
        status=200,
        mimetype='application/json'
    )
    return response

if __name__ == "__main__":
    app.run()