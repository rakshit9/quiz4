import os
from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import InputRequired
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import nltk
import codecs
from collections import defaultdict
from time import time
from collections import Counter
import re  # Regular expression library for splitting text into words


app = Flask(__name__)


nltk.download(['punkt', 'stopwords'])
porter = PorterStemmer()


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecureSecretKey'
app.config['UPLOAD_FOLDER'] = 'static'
app.config['UPDATED_FILES'] = 'static/updated_data'
app.config['ALLOWED_EXTENSIONS'] = {'txt'}
app.config['STOPWORDS_FILE'] = 'static/StopWords.txt'



@app.route('/', methods=['GET', 'POST'])
def main():
    try:
        msg = "Welcome to Search Engine!"
        return render_template('index.html', error=msg)
    except Exception as e:
        return render_template('index.html', error=e)

def load_stopwords(file_path):
    with codecs.open(file_path, 'r', encoding='utf-8') as f:
        stopwords_list = f.read().split()
    return set(stopwords_list)

# stop_words = set(stopwords.words(['english', 'spanish', 'french']))
stop_words = load_stopwords(app.config['STOPWORDS_FILE'])


ps = PorterStemmer()


def preprocess_text(input_file, output_file):
    with codecs.open(input_file, 'r', encoding='utf-8') as f:
        text = f.read()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


class UploadForm(FlaskForm):
    textfile = FileField('Text File', validators=[
        FileRequired(),
        FileAllowed(app.config['ALLOWED_EXTENSIONS'], 'Text files only!')
    ])
    submit = SubmitField('Upload and Process')


def process_text(text):
    processed_text = []
    lines = text.split('\n')
    for i, line in enumerate(lines):
        words = word_tokenize(line)
        words = [word.lower() for word in words if word.isalpha()]
        words = [word for word in words if not word in stop_words]
        words = [porter.stem(word) for word in words]
        processed_line = ' '.join(words)
        processed_text.append(f"{i+1}: {processed_line}")
    return '\n'.join(processed_text)


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    success_message = ""
    form = UploadForm()
    if form.validate_on_submit():
        f = form.textfile.data
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            f.save(file_path)
            with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                text = file.read()
                processed_text = process_text(text)
                updated_file_path = os.path.join(app.config['UPDATED_FILES'], filename)
                with codecs.open(updated_file_path, 'w', encoding='utf-8') as new_file:
                    new_file.write(processed_text)
                success_message = f"File uploaded and processed successfully. The filename is: {filename}"
    return render_template('upload.html', form=form, success_message=success_message)


class SearchForm(FlaskForm):
    query = StringField('Search Query', [InputRequired()])
    submit = SubmitField('Search')


def process_query(query):
    words = word_tokenize(query)
    words = [word.lower() for word in words if word.isalpha()]
    words = [word for word in words if not word in stop_words]
    words = [porter.stem(word) for word in words]
    return words


@app.route('/search', methods=['GET', 'POST'])
def search():
    form = SearchForm()
    results = defaultdict(list)
    start_time = time()
    if form.validate_on_submit():
        query = form.query.data
        query = process_query(query)
        for filename in os.listdir(app.config['UPDATED_FILES']):
            file_path = os.path.join(app.config['UPDATED_FILES'], filename)
            with codecs.open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = file.readlines()
                for i, line in enumerate(lines):
                    words = line.split()
                    if words and any(word in words for word in query):
                        results[filename].append((i+1, line))
        results = {k: v for k, v in results.items() if v}
        if not results:
            flash("No results found for your query.", "danger")
    elapsed_time = time() - start_time
    return render_template('search.html', form=form, results=results, elapsed_time=elapsed_time)


@app.route('/char_operations', methods=['GET', 'POST'])
def char_operations():
    if request.method == 'POST':
        s = request.form['string_s']
        c = request.form['char_c']
        t = request.form['text_t']

        # Ensure that `s` is between 1 to 10 characters and `c` is exactly 1 character
        if not (1 <= len(s) <= 10 and len(c) == 1):
            return render_template('char_operations.html', error="Ensure 'S' is 1-10 characters long and 'C' is a single character.")

        # Character counting and frequency calculation
        counts = Counter(t)
        character_count = {char: counts[char] for char in s}
        total_chars = sum(counts.values())
        frequency = {char: (counts[char] / total_chars) for char in s if total_chars > 0}

        # Replacement operation
        replaced_text = ''.join([c if char in s else char for char in t])

        return render_template('char_operations.html', character_count=character_count, frequency=frequency, replaced_text=replaced_text)
    
    else:  # This else part ensures that there's always a return for GET requests
        return render_template('char_operations.html')

@app.route('/word_operations', methods=['GET', 'POST'])
def word_operations():
    if request.method == 'POST':
        s = request.form['string_s']
        t = request.form['text_t']

        # Splitting text T into words using regular expressions
        words = re.findall(r'\b\w+\b', t)
        word_count = len(words)

        # Dictionary to hold lists of words starting with each character in S
        starting_words = {char: [] for char in s}

        # Populate the dictionary with words starting with each character
        for word in words:
            for char in s:
                if word.lower().startswith(char.lower()):  # Case insensitive matching
                    starting_words[char].append(word)

        return render_template('word_operations.html', word_count=word_count, starting_words=starting_words)
    
    return render_template('word_operations.html')


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)