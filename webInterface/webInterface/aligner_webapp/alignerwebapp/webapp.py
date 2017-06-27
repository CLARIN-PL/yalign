import json
import logging
import os
import re
import sqlite3
import time
from random import SystemRandom
from functools import wraps
from datetime import datetime
from flask import Flask, request, g, make_response, abort, Response
from werkzeug.utils import secure_filename
from workq import db
from workq.workq import WorkQ

system_random = SystemRandom()
app = Flask('alignerwebapp')
app.config.update(
    work_db=None,
    yalign_models=None,
    data_path=None
)
log = logging.getLogger(__name__)
user_id_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'

def auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'token' in request.args:
            return f(*args, **kwargs)
        else:
            # todo: on error json response
            abort(401)
    return wrapper

def generate_user_id():
    user_id = ''
    for _ in range(32):
        user_id += system_random.choice(user_id_chars)
    return user_id

def get_workq():
    if not hasattr(g, 'workq'):
        g.workq = WorkQ(app.config['work_db'], app.config['data_path'])
    return g.workq

def get_user_id():
    """TODO: Docstring for get_user_id.
    :returns: TODO

    """
    return request.args['token']

def isotime_from_timestamp(ts):
    d = datetime.utcfromtimestamp(ts)
    return d.isoformat()

def get_task_dict(task):
    result = None
    if task['result']:
        result = '/api/tasks/{}/result'.format(task['id'])
    return {
        'id': task['id'],
        'status': task['status'],
        'data': json.loads(task['data']),
        'created_time': isotime_from_timestamp(task['created_time']),
        'result': result
    }

def get_user_dict(user):
    """TODO: Docstring for get_user_dict.

    :user: TODO
    :returns: TODO

    """
    return {
        'id': user['id']
    }

def get_response(data):
    """TODO: Docstring for get_response.

    :data: TODO
    :returns: TODO

    """
    data = json.dumps(data)
    response = make_response(data, 200)
    response.mimetype = 'application/json'
    return response

def get_list_response(data):
    """TODO: Docstring for get_list_response.

    :data: TODO
    :returns: TODO

    """
    data = {
        'data': data
    }
    return get_response(data)

@app.route('/', methods=['GET'])
def index():
    """TODO: Docstring for index.
    :returns: TODO

    """
    return app.send_static_file('index.html')

@app.route('/api/ping', methods=['GET'])
def get_ping():
    return get_response({'pong': 'pong'})

@app.route('/api/users/signin', methods=['POST'])
def post_users_signin():
    """TODO: Docstring for post_users_signin.
    :returns: TODO

    """
    return get_response(get_user_dict({'id': generate_user_id()}))

@app.route('/api/tasks', methods=['POST'])
@auth
def post_tasks():
    """Creates new task

    :returns: TODO

    """
    workq = get_workq()
    task = workq.create_task(
        get_user_id(),
        request.get_json()
    )
    return get_response(get_task_dict(task))

@app.route('/api/me/tasks', methods=['GET'])
@auth
def get_me_tasks():
    """TODO: Docstring for get_me_tasks.
    :returns: TODO

    """
    tasks = get_workq().get_user_tasks(get_user_id())
    tasks = [get_task_dict(t) for t in tasks]
    return get_list_response(tasks)

@app.route('/api/langpairs', methods=['GET'])
@auth
def get_langpairs():
    """TODO: Docstring for get_langpairs.
    :returns: TODO

    """
    models = os.listdir(app.config['yalign_models'])
    models = [m.split('-', maxsplit=1) for m in models if '-' in m]
    return get_list_response(
        models
    )

@app.route('/api/tasks/<int:task_id>/<pair_id>/<lang>/inputpairs', methods=['POST'])
@auth
def post_tasks_by_id_by_pair_id_by_lang_inputpairs(task_id, pair_id, lang):
    workq = get_workq()
    pair_id = pair_id.lower()
    lang = lang.lower()
    task = workq.get_task(task_id)
    if task['status'] != db.STATUS_PREPARE:
        abort(400)
    if len(request.files) == 0:
        abort(400)
    uploaded_file = next(request.files.values())
    workq.add_input_file(task_id, pair_id, lang, uploaded_file.filename, uploaded_file)
    return ''

@app.route('/api/tasks/<int:id_>/enqueued', methods=['PUT'])
@auth
def put_tasks_by_id_enqueued(id_):
    """TODO: Docstring for put_tasks_by_id_enqueued.

    :id_: TODO
    :returns: TODO

    """
    workq = get_workq()
    task = workq.get_task(id_)
    if task['status'] not in [db.STATUS_PREPARE, db.STATUS_ENQUEUED]:
        abort(400)
    task = workq.set_status(id_, db.STATUS_ENQUEUED)
    return get_response(get_task_dict(task))

@app.route('/api/tasks/<int:id_>/result', methods=['GET'])
@auth
def get_tasks_by_id_result(id_):
    """TODO: Docstring for get_tasks_by_id_result.

    :id_: TODO
    :returns: TODO

    """
    def stream(path):
        with open(path, 'rb') as f:
            while True:
                next_data = f.read(16384)
                if not next_data:
                    break
                yield next_data
    path = get_workq().get_task_result_path(get_user_id(), id_)
    if not path:
        abort(404)
    response = Response(stream(path), mimetype='application/zip')
    response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(
        os.path.basename(path)
    )
    return response
