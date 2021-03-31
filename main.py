import argparse
import re
import os

from flask import Flask, render_template, request, jsonify, url_for
from werkzeug.utils import secure_filename

from handler.lex_process import KaldiLexiconHandler
from celery_queue.workers import compile_hclg

LEX_PATH = 'lexicon.txt'
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = ("txt")

lex_handler = KaldiLexiconHandler(LEX_PATH)

''' Flask '''
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


'''  Disable Cache  '''
@app.after_request
def add_header(response):
    response.headers['Pragma'] = 'no-cache'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = '0'
    response.cache_control.public = True
    response.cache_control.max_age = 0

    return response


@app.route('/')
def home():  # home page
    return render_template('index.html')  # return html file


def is_valid_input(input_word, lang):  # check input and lang
    # Empty
    if not input_word:
        return False

    # Check space
    if input_word != ''.join(input_word.split()):
        return False

    # Check lang
    if lang == 'zh':
        patten = re.compile(u'[\u4e00-\u9fff]+')
        if not re.search(patten, input_word):
            return False
    elif lang == 'en':
        patten = re.compile(r'[a-zA-Z]+')
        if not re.fullmatch(patten, input_word):
            return False
    else:
        return False
    return True


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def add_word(input_word, lang):
    if is_valid_input(input_word, lang):
        if not lex_handler.isexisted(input_word):
            # Generate prons
            prons = lex_handler.generate_prons(input_word, lang)

            # Check if prons empty
            if not prons:
                return False, '無法產生拼音！'

            # Write lexicon.txt
            lex_handler.write_lexicon(LEX_PATH, input_word, prons)

            # Update lexicon vars
            lex_handler.add_lexicon(input_word, prons)

            return True, '字詞加入成功！'
        else:
            return False, '字詞已存在!'
    else:
        return False, '字詞包含不當字元或為空！'

@app.route('/add', methods=['POST'])
def add_words():
    lang = request.form['lang']
    ignore = {}

    if 'words' in request.files:
        # Get file
        file = request.files['words']

        # Check file type
        if not allowed_file(file.filename):
            return render_template('index.html', result='非允許檔案類型！')

        # Clear filename
        filename = secure_filename(file.filename)

        # Save file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Generate prons
        for line in open(file_path, 'r', encoding='utf-8'):
            input_word = line.replace('\n', '')
            success, msg = add_word(input_word, lang)
            if not success:
                ignore[input_word] = msg

        # Write the skip words and msg
        if ignore:
            with open('log_ignore.txt', 'a', encoding='utf-8') as f:
                for key in ignore.keys():
                   f.write('{}:{}\n'.format(key, ignore[key]))
            return render_template('index.html', result='部分字詞未能加入！')

        return render_template('index.html', result='全部字詞加入成功！')

    else:
        input_word = request.form['input']
        success, msg = add_word(input_word, lang)
        return render_template('index.html', result=msg)


@app.route('/delete')
def delete_words():
    pass


@app.route('/search')
def search_word():
    pass


@app.route('/update')
def update_word():
    pass


@app.route('/compile', methods=['POST'])
def compile_lexicon():
    task = compile_hclg.apply_async()
    return jsonify({'message': '已接收請求！', 'Location': url_for('task_status', task_id=task.id)}), 202


@app.route('/status/<task_id>')
def task_status(task_id):
    task = compile_hclg.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'Status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'Stage': task.info.get('Stage', 0),
            'Total': task.info.get('Total', 1),
            'Status': task.info.get('Status', '')
        }
    else:  # state == FAILURE
        response = {
            'state': task.state,
            'Stage': 'Task fail',
            'Total': 4,
            'Status': str(task.info)
        }
    return jsonify(response)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Simple Lexadder flask service')
    parser.add_argument('-host', help='Set host ip', dest='host', default='127.0.0.1')
    parser.add_argument('-port', help='Set port number', dest='port', default=5000, type=int)

    args = parser.parse_args()

    from waitress import serve
    serve(app, host=args.host, port=args.port)
    #app.run(host=args.host, port=args.port, debug=True)  # Set debug mode when developing
