import os
import unittest
import tempfile
import shutil
import json
import io
from alignerwebapp.webapp import app
from workq import db

def api_post(client, url, data, params=None, user=None):
    data = json.dumps(data)
    if params is None:
        params = {}
    if user:
        params['token'] = user['id']
    response = client.post(url, query_string=params, data=data, content_type='application/json')
    return json.loads(response.data.decode('utf-8')), response.status_code

def api_put(client, url, data=None, user=None):
    params = {}
    if user:
        params['token'] = user['id']
    if data is not None:
        data = json.dumps(data)
    response = client.put(url, query_string=params, data=data, content_type='application/json')
    return json.loads(response.data.decode('utf-8')), response.status_code

def api_post_files(client, url, data, user=None):
    params = {}
    if user:
        params['token'] = user['id']
    response = client.post(url, query_string=params, data=data, content_type='multipart/form-data')
    return response.status_code

class TestApi(unittest.TestCase):

    """Docstring for TestApi. """

    def setUp(self):
        """TODO: Docstring for setUp.
        :returns: TODO

        """
        tmp_work_db_handler, tmp_work_db_path = tempfile.mkstemp()
        os.close(tmp_work_db_handler)
        db.init_db(tmp_work_db_path)
        app.config.update(
            work_db=tmp_work_db_path,
            data_path=tempfile.mkdtemp()
        )
        self.client = app.test_client()

    def tearDown(self):
        """TODO: Docstring for tearDown.
        :returns: TODO

        """
        os.unlink(app.config['work_db'])
        shutil.rmtree(app.config['data_path'])

    def test_post_users_signin(self):
        """TODO: Docstring for test_post_users_signin.
        :returns: TODO

        """
        user, code = api_post(self.client, '/api/users/signin', {})
        self.assertEqual(code, 200)
        self.assertEqual(len(user['id']), 32)

    def test_post_tasks(self):
        """TODO: Docstring for test_post_tasks.
        :returns: TODO

        """
        user, code = api_post(self.client, '/api/users/signin', {})
        task, code = api_post(self.client, '/api/tasks', {'task_data': 'some_data'}, user=user)
        self.assertEqual(code, 200)
        self.assertTrue(task['id'] >= 0)
        self.assertEqual(task['status'], db.STATUS_PREPARE)
        self.assertEqual(task['data']['task_data'], 'some_data')

    def test_post_tasks_by_id_inputpairs(self):
        """TODO: Docstring for test_post_tasks_by_id_inputpairs.
        :returns: TODO

        """
        user, code = api_post(self.client, '/api/users/signin', {})
        task, code = api_post(self.client, '/api/tasks', {'task_data': 'some_data'}, user=user)
        code = api_post_files(
            self.client,
            '/api/tasks/{}/1/en/inputpairs'.format(task['id']),
            {
                'en': (io.BytesIO(b'eeeeeee'), 'en.txt')
            },
            user=user
        )
        self.assertEqual(code, 200)
        code = api_post_files(
            self.client,
            '/api/tasks/{}/1/ru/inputpairs'.format(task['id']),
            {
                'ru': (io.BytesIO(b'rrrrrrr'), 'ru.txt')
            },
            user=user
        )
        self.assertEqual(code, 200)

    def test_post_tasks_by_id_enqueued(self):
        """TODO: Docstring for test_post_tasks_by_id_enqueued.
        :returns: TODO

        """
        user, code = api_post(self.client, '/api/users/signin', {})
        task, code = api_post(self.client, '/api/tasks', {}, user=user)
        task, code = api_put(self.client, '/api/tasks/{}/enqueued'.format(task['id']), user=user)
        self.assertEqual(code, 200)
        self.assertEqual(task['status'], db.STATUS_ENQUEUED)
