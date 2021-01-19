import subprocess
from celery import Celery

CELERY_BROKER_URL = 'redis://127.0.0.1:6379'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379'


''' Celery '''
celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)
#celery.conf.update(app.config)

@celery.task(bind=True)
def compile_hclg(self):
    ''' Call kaldi script '''

    scripts = ['scripts/prepare_lex.sh',
     'scripts/prepare_phone.sh',
     'scripts/compile_LG.sh',
     'scripts/compile_graph.sh']
    error_res = {'Stage': 'Execute Fail',
                'Total': len(scripts)}

    for i, script in enumerate(scripts):
        try:
            ret = subprocess.run(script)
            if ret.returncode == 0:
                self.update_state(state='PROGESS',
                                      meta={'Stage': i+1, 'Total': len(scripts),
                                            'Status': 'Finish {}/{} stage'.format(i+1, len(scripts))})
            else:
                print('{} is executed but something go wrong'.format(script))
                error_res['Status'] = '{} is executed but something go wrong'.format(script)
                return error_res
        except:
            print('Unexcepted error, fail in {}'.format(script))
            error_res['Status'] = 'unexcepted error, fail in {}'.format(script)
            return error_res

    return {'Stage': len(scripts), 'Total': len(scripts),
            'Status': 'All done!'}