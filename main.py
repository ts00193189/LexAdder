import time
import os


from flask import Flask, render_template, request, jsonify, url_for
from celery import Celery, result

from lex_process import KaldiLexiconHandler

LEX_PATH = 'lexicon.txt'
SCRIPT_PATH = 'D:\PycharmProjects\flask-kaldi\scripts\test.bat'

lex_handler = KaldiLexiconHandler(LEX_PATH)

''' Flask '''

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://127.0.0.1:6379'
app.config['CELERY_RESULT_BACKEND'] = 'redis://127.0.0.1:6379'


''' Celery '''
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'], backend=app.config['CELERY_RESULT_BACKEND'])
#celery.conf.update(app.config)

@celery.task(bind=True)
def compile_hclg(self):
    self.update_state()

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

                # Call kaldi script
                #lex_handler.recompile_hclg(SCRIPT_PATH)

                return render_template('index.html', result='字詞加入成功')
            else:
                return render_template('index.html', result='字詞已存在')
        elif request.form['lang'] == 'en':
            pass
    else:
        return render_template('index.html', result='字詞與語言不符')

@app.route('/delete')
def delete_words():
    pass


@app.route('/search', methods=['POST'])
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
    #res = compile_hclg.AsyncResult(task.id)

    #print(task.state)
    #print(task.get())
    #return jsonify({'message':'已接收請求！'}), 202
    return jsonify({'message':'已接收請求！'}), 202, {'Location': url_for('task_status', task_id=task.id)}

@app.route('/status/<task_id>')
def task_status(task_id):
    task = compile_hclg.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status':'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'Stage': task.info.get('Stage', 0),
            'Total': task.info.get('Total', 1),

            'status': task.info.get('status', '')
        }
    else:
        response = {
            'state': task.state,
            'Stage': 1,
            'Total': 1,

            'status': str(task.info)
        }
    return jsonify(response)

if __name__ == '__main__':
    '''global lexicon
    lexicon = build_lexicon()'''
    app.run(host='127.0.0.1', port=5000, debug=True) # Set debug mode when developing