import string

from flask import Flask, render_template, request, jsonify
from error_checker import get_error
from ngram import Ngram
from bert import get_correction_suggestions
import psycopg2

app = Flask(__name__)

con = psycopg2.connect(database="ngrams", user="postgres", password="xgqSHThRHP4mOioFVFSh", host="postgres", port="5432",
                       sslmode="disable")


def init_db(connection):
    cur = connection.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS ngram_en(ngram text NOT NULL, count double precision, year integer NOT NULL, CONSTRAINT ngramen_pkey PRIMARY KEY (year, ngram));"
        "CREATE TABLE IF NOT EXISTS ngram_de(ngram text NOT NULL, count double precision, year integer NOT NULL, CONSTRAINT ngramde_pkey PRIMARY KEY (year, ngram));")
    connection.commit()
    cur.close()


def parse_sentence(data):
    user_input = data['content']
    language = data['language']
    sentence_end = ""
    if user_input[-1:] in string.punctuation:
        sentence_end = user_input[-1:]
    user_input = ''.join(ch for ch in user_input if ch not in set(string.punctuation))
    return user_input, language, sentence_end


def build_response_sentence(mistakes, tokens, language, sentence_end, values):
    response_tokens = tokens.copy()
    for mistake in mistakes:
        variant_tokens = tokens.copy()
        variant_tokens[mistake] = '[MASK]'
        bert_results = get_correction_suggestions(" ".join(variant_tokens) + sentence_end, tokens[mistake], mistake, language, con)
        response_tokens[mistake] = '<mark id="' + str(mistake) + '" suggestions="' + \
                                   " ".join(bert_results["token_strs"]) + '" scores="' + \
                                   " ".join(['{:.3f}'.format(x) for x in bert_results["scores"]]) + \
                                   '" ranks="' + " ".join(['{:.3f}'.format(x) for x in bert_results["ranks"]]) + \
                                   '">' + tokens[mistake] + '</mark>'
    debug_box = ""
    for i in values:
        debug_box += "<span>" + i + " : " + str(values[i]) + "</span>"
    return " ".join(response_tokens) + sentence_end, debug_box


@app.route('/')
def hello():
    return render_template("grammar.html")


@app.route('/background_check', methods=['POST'])
def background_process():
    if request.method == 'POST':
        user_input, language, sentence_end = parse_sentence(request.get_json())
        if user_input == "":
            return jsonify("")

        tokens = user_input.split()
        sentence = Ngram(language, con, user_input)
        values = sentence.values
        mistakes = get_error(user_input, values)

        response_sentence, debug_box = build_response_sentence(mistakes, tokens, language, sentence_end, values)

        data = {"content": response_sentence, "errorcount": str(len(mistakes)),
                "ngramcounts": debug_box,
                "tokencount": str(len(user_input + sentence_end)),
                "wordcount": str(len(tokens))}
        return jsonify(data)


@app.route('/background_check_debug', methods=['POST'])
def background_process_debug():
    return 'debug'


if __name__ == "__main__":
    init_db(con)
    app.run(host="0.0.0.0", debug=True)
