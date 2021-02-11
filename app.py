from flask import Flask, render_template, request
import model
import database

app = Flask(__name__)


@app.route('/')
def index():
    return render_template("grammar.html")


@app.route('/grammar_check', methods=['POST'])
def grammar_check():
    data = request.get_json()
    ngram_model = model.Model(data['content'], data['language'])
    response = ngram_model.build_response()

    return response


if __name__ == "__main__":
    db = database.Database.instance()
    db.init_table()
    app.run(host="0.0.0.0", debug=True)
