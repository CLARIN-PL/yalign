import sqlite3
import time
import logging
import os
import json
import uuid
import shutil
from workq import db

class WorkQ(object):

    """Docstring for WorkQ. """

    _cursor = None
    _con = None
    log = logging.getLogger(__name__)

    @property
    def con(self):
        if self._con is None:
            self._con = sqlite3.connect(self.db_path)
            self._con.row_factory = sqlite3.Row
            # enable support for foreign key constraint
            self._con.execute('PRAGMA foreign_keys = ON;')
        return self._con

    @property
    def cursor(self):
        """TODO: Docstring for cursor.
        :returns: TODO

        """
        if self._cursor is None:
            self._cursor = self.con.cursor()
        return self._cursor

    def __init__(self, db_path, data_path):
        self.db_path = db_path
        self.data_path = os.path.abspath(data_path)

    def get_task(self, id_):
        return self.cursor.execute('select * from tasks where id = ?', (id_,)).fetchone()

    def create_task(self, user_id, data):
        with self.con:
            # creating separate cursor to keep thread safe, cursor will have correct
            # lastrowid
            cursor = self.con.cursor()
            cursor.execute(
                'insert into tasks (user, status, data, created_time) values (?, ?, ?, ?)',
                (user_id, db.STATUS_PREPARE, json.dumps(data), int(time.time()))
            )
            task = cursor.execute('select * from tasks where rowid = ?', (cursor.lastrowid,)).fetchone()
        return task

    def get_user_tasks(self, user_id):
        """TODO: Docstring for get_user_tasks.

        :user_id: TODO
        :returns: TODO

        """
        return self.cursor.execute('select * from tasks where user = ? order by created_time desc', (user_id,)).fetchall()

    def get_task_file_dir(self, task_id):
        """TODO: Docstring for get_task_file_dir.

        :task_id: TODO
        :returns: TODO

        """
        path = os.path.join(self.data_path, str(task_id))
        if not os.path.exists(path):
            self.log.info('Creating task file directory: %s', path)
            os.mkdir(path)
        return path

    def get_input_pairs_dir(self, task_id):
        """TODO: Docstring for get_input_pairs_dir.

        :task_id: TODO
        :returns: TODO

        """
        path_dir = self.get_task_file_dir(task_id)
        path_dir = os.path.join(path_dir, 'input_pairs')
        if not os.path.exists(path_dir):
            self.log.info('First file in task input, creating directory: %s', path_dir)
            os.mkdir(path_dir)
        return path_dir

    def add_input_file(self, task_id, pair_id, lang, name, storage):
        """
        Input pairs saved at [data_path]/[task_id]/input_pairs/[pair_id]/[lang]/[file_name]
        """
        path_dir = self.get_input_pairs_dir(task_id)
        path_dir = os.path.join(path_dir, pair_id)
        if not os.path.exists(path_dir):
            os.mkdir(path_dir)
        path_dir = os.path.join(path_dir, lang)
        os.mkdir(path_dir)
        path = os.path.join(path_dir, name)
        self.log.info('Saving task %s file to %s', task_id, path)
        storage.save(path)

    def _update_status(self, task_id, status):
        self.cursor.execute('update tasks set status = ? where id = ?', (status, task_id))

    def set_status(self, task_id, status):
        """TODO: Docstring for set_status.

        :task_id: TODO
        :status: TODO
        :returns: TODO

        """
        with self.con:
            self._update_status(task_id, status)
        return self.get_task(task_id)

    def start_next_task(self):
        """TODO: Docstring for start_next_task.
        :returns: TODO

        """
        with self.con:
            self.cursor.execute('begin')
            task = self.cursor.execute('select * from tasks where status = ? limit 1', (db.STATUS_ENQUEUED,)).fetchone()
            if not task:
                return None
            self._update_status(task['id'], db.STATUS_INPROGRESS)
        return task

    def _get_result_path(self, task_id, result_name):
        """TODO: Docstring for _get_result_path.

        :task_id: TODO
        :returns: TODO

        """
        path = self.get_task_file_dir(task_id)
        return os.path.join(path, result_name)

    def complete_task_with_result(self, task_id, result_path):
        """TODO: Docstring for complete_task_with_result.

        :task_id: TODO
        :result_path: TODO
        :returns: TODO

        """
        result_name = os.path.basename(result_path)
        shutil.copyfile(result_path, self._get_result_path(task_id, result_name))
        with self.con:
            self.cursor.execute('update tasks set result = ? where id = ?', (result_name, task_id))
        return self.set_status(task_id, db.STATUS_READY)

    def get_task_result_path(self, user_id, task_id):
        """TODO: Docstring for get_task_result_path.

        :user_id: TODO
        :task_id: TODO
        :returns: TODO

        """
        task = self.cursor.execute('select * from tasks where user = ? and id = ?', (user_id, task_id)).fetchone()
        if not task:
            return None
        path = self.get_task_file_dir(task['id'])
        path = os.path.join(path, task['result'])
        return path

    def iter_input_pairs(self, task_id):
        """TODO: Docstring for iter_input_pairs.

        :task_id: TODO
        :returns: TODO

        """
        path = self.get_input_pairs_dir(task_id)
        for next_name in os.listdir(path):
            next_path = os.path.join(path, next_name)
            pair = {}
            for next_lang in os.listdir(next_path):
                next_lang_path = os.path.join(next_path, next_lang)
                for next_file_name in os.listdir(next_lang_path):
                    pair[next_lang] = os.path.join(next_lang_path, next_file_name)
            yield pair
