from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
from nltk.tokenize import RegexpTokenizer, word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import string
from flask import jsonify
from collections import Counter
#nltk.download('punkt')


app = Flask(__name__)
app.config['SECRET_KEY'] = 'SecureSecretKey'


# def cleanfile():
#     files = []
#     for i in os.listdir('static'):
#         if i.endswith('.txt'):
#             files.append(i)

#     ps = PorterStemmer()
#     token = RegexpTokenizer(r'\w+')

#     for i in files:
#         path = f'static\{i}'

#         with open(path, encoding='utf8') as file:
#             a = file.read()
#             a = a.replace("\n", "q1q1s1")
#             t1 = token.tokenize(a)
#             filtered_words = [w for w in t1 if not w in stopwords.words('english')]
#             a = " ".join(filtered_words)
#             temp = word_tokenize(a)
#             ar = []
#             for j in temp:
#                 ar.append(ps.stem(j))
#             a1 = " ".join(ar)
#             a = a1.replace("q1q1s1", "\n")

#         path = f'static\clean_files\{i}'

#         with open(path, 'w',  encoding='utf8') as out:
#             out.writelines(a)


@app.route('/', methods=['GET', 'POST'])
def main():
    try:
        cnt = 0
        if cnt == 0:
            #cleanfile()
            cnt = 1

        return render_template('index.html')
    except Exception as e:
        return render_template('index.html', error=e)


# class Form1(FlaskForm):
#     s = StringField(label='Enter Word: ', validators=[DataRequired()])
#     submit = SubmitField(label='Search')


# @app.route('/form1', methods=['GET', 'POST'])
# def form1():
#     form = Form1()
#     if form.validate_on_submit():
#         try:
#             search_word = form.s.data

#             search_file = []
#             search_line_num = []
#             search_line = []
#             clean_files = []
#             final_cnt = 0
#             final = []

#             for i in os.listdir('static\clean_files'):
#                 if i.endswith('.txt'):
#                     clean_files.append(i)

#             for i in clean_files:
#                 path = f'static\clean_files\{i}'
#                 tot_cnt = 0
#                 with open(path, encoding='utf8') as file:
#                     lines = file.readlines()
#                     for j in lines:
#                         tot_cnt += 1
#                         if search_word in j:
#                             if i not in search_file:
#                                 search_file.append(i)
#                                 final.append(final_cnt)
#                             final_cnt += 1
#                             search_line_num.append(tot_cnt)
#                             search_line.append(j.strip())

#             return render_template('form1.html', search_line=search_line, search_line_len=len(search_line), search_line_num=search_line_num, search_line_num_len=len(search_line_num), search_file=search_file, search_file_len=len(search_file), final=final, form=form, search_word=search_word, data=1)

#         except Exception as e:
#             print(e)
#             return render_template('form1.html', form=form, error=e)

#     return render_template('form1.html', form=form)


def process_text_file(file_path):
    try:
     
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            text = file.read()

    text = text.lower()  # Convert text to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation))  # Remove punctuation

    letters_count = sum(c.isalpha() for c in text)
    
    words_count = len(text.split())

    return letters_count, words_count



@app.route('/process_file')
def process_file():
    try:
        file_path = os.path.join('static', 'u.txt')
        letters_count, words_count = process_text_file(file_path)
        
        return jsonify({
            'Total Letters': letters_count,
            'Total Words': words_count
        })
    except Exception as e:
        return str(e), 400



def count_vowels(file_path):
    vowels = 'aeiou'
    try:
        # Try opening the file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read().lower()
    except UnicodeDecodeError:
        # If UTF-8 fails, fall back to ISO-8859-1
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            text = file.read().lower()

    vowel_count = Counter(char for char in text if char in vowels)
    return vowel_count

@app.route('/compare_vowels')
def compare_vowels():
    try:

        u_path = os.path.join('static', 'u.txt')
        s_path = os.path.join('static', 's.txt')
        f_path = os.path.join('static', 'f.txt')

        u_vowels = count_vowels(u_path)
        s_vowels = count_vowels(s_path)
        f_vowels = count_vowels(f_path)

        s_diff = sum(abs(u_vowels[v] - s_vowels[v]) for v in 'aeiou')
        f_diff = sum(abs(u_vowels[v] - f_vowels[v]) for v in 'aeiou')

        more_similar = 's.txt' if s_diff < f_diff else 'f.txt'
        return jsonify({
            'u.txt Vowel Count': dict(u_vowels),
            's.txt Vowel Count': dict(s_vowels),
            'f.txt Vowel Count': dict(f_vowels),
            'More Similar File': more_similar
        })
    except Exception as e:
        return str(e), 400


def remove_short_words(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='iso-8859-1') as file:
            text = file.read()

    words = text.split()
    filtered_words = [word for word in words if len(word) > 3]
    modified_text = ' '.join(filtered_words)

    return modified_text

@app.route('/process_u_txt')
def process_u_txt():
    file_path = os.path.join('static', 'u.txt')
    modified_text = remove_short_words(file_path)
    return modified_text


if __name__ == "__main__":
    app.run(debug=True, port=5000)