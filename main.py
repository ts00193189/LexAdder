from flask import Flask, render_template, request, jsonify, url_for

from handler.lex_process import KaldiLexiconHandler
from celery_queue.workers import compile_hclg

LEX_PATH = 'lexicon.txt'

lex_handler = KaldiLexiconHandler(LEX_PATH)

''' Flask '''
app = Flask(__name__)


@app.route('/')
def home(): #  home page
    return render_template('index.html') # return html file


def is_valid_input(input_word, lang): #check input and lang
    return True


@app.route('/add', methods=['POST'])
def add_words():
    lang = request.form['lang']
    input_word = request.form['input']

    if is_valid_input(input_word, lang):
        #lex_table = build_lexicon()
        if lang == 'zh':
            if not lex_handler.isexisted(input_word):

                # Generate prons
                prons = lex_handler.generate_prons(input_word)

                # Write lexicon.txt
                lex_handler.write_lexicon(LEX_PATH, input_word, prons)

                # Update lexicon vars
                lex_handler.add_lexicon(input_word, prons)

                return render_template('index.html', result='字詞加入成功！')
            else:
                return render_template('index.html', result='字詞已存在！')
        elif request.form['lang'] == 'en':
            return 'Not implement'
    else:
        return render_template('index.html', result='字詞與選擇語言不符！')
        #return jsonify({'message': '字詞與選擇語言不符！'})

@app.route('/delete')
def delete_words():
    pass


@app.route('/search', methods=['POST', 'GET'])
def search_word():
   ''' target = request.form['input']
    lex_table = build_lexicon()

    if target in lex_table:
        print('{} {}'.format(target, lex_table[target]))
        return render_template('index.html', result={target:lex_table[target]})
    else:
        print('字詞不存在')
        return render_template('index.html', result='字詞不存在')'''
   pass


@app.route('/update')
def update_word():
    pass


@app.route('/compile', methods=['POST', 'GET'])
def compile_lexicon():

    task = compile_hclg.apply_async()
    return jsonify({'message':'已接收請求！'}), 202, {'Location': url_for('task_status', task_id=task.id)}

@app.route('/status/<task_id>')
def task_status(task_id):
    task = compile_hclg.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'Status':'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'Stage': task.info.get('Stage', 0),
            'Total': task.info.get('Total', 1),

            'Status': task.info.get('Status', '')
        }
    else: # state == FAILURE
        response = {
            'state': task.state,
            'Stage': 'Task fail',
            'Total': 4,

            'Status': str(task.info)
        }
    return jsonify(response)

if __name__ == '__main__':

    app.run(host='127.0.0.1', port=5000, debug=True) # Set debug mode when developing