from flask import Flask, render_template, url_for, request, redirect
from main import check_word

app = Flask(__name__)

@app.route('/', methods=['POST','GET'])
def index():
    return render_template('index.html')

@app.route('/definition/', methods=['POST', 'GET'])
def find_definition():
    dictionary_name = request.form.get('dictionary_name')
    language_from = request.form.get('language_from')
    language_to = request.form.get('language_to')
    word = request.form.get('word')
    words, examples = check_word(dictionary_name, language_from, language_to, word)

    if len(words) == 1 and words[0].key == 'Word not found!':
        error_statement = 'Word not found!'
        return render_template('index.html', 
            error_statement=error_statement)

    return render_template('definition.html', words=words, examples=examples)

@app.route('/definition/<dictionary_name>/<language_from>/<language_to>/<word>', methods=['POST', 'GET'])
def find_word(dictionary_name, language_from, language_to, word):
    words, examples = check_word(dictionary_name, language_from, language_to, word)
    return render_template('definition.html', words=words, examples=examples)


if __name__ == '__main__':
    app.run(debug=True)

