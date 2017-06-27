#!/usr/bin/env python3

import os
import subprocess
import threading
import logging
from argparse import ArgumentParser
from workq import db

_readme = """
"""
_readme = _readme.strip()

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
log = logging.getLogger('aligner')
work_dir = os.path.dirname(os.path.abspath(__file__))

def get_conf():
    parser = ArgumentParser(description='', usage=_readme)
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    return parser.parse_args()

def get_path(path):
    return os.path.join(work_dir, path)

def main():
    conf = get_conf()
    log.info('Starting Web UI')

    os.chdir(os.path.dirname(__file__))

    if not os.path.exists(get_path('work.db')):
        log.info('Initializing work DB')
        db.init_db(get_path('work.db'))
    if not os.path.exists(get_path('_data')):
        log.info('Creating directory for task files')
        os.mkdir(get_path('_data'))

    if not os.path.exists(get_path('ve')):
        subprocess.call([
            'virtualenv',
            '-p',
            'python3',
            get_path('ve')
        ])
        subprocess.call([
            get_path('ve/bin/pip'),
            'install',
            'pip',
            '-U'
        ])
        subprocess.call([
            get_path('ve/bin/pip'),
            'install',
            '-r',
            get_path('requirements_web.txt')
        ])

    if not os.path.exists(get_path('yalignve')):
        subprocess.call([
            'virtualenv',
            '-p',
            'python2',
            get_path('yalignve')
        ])
        subprocess.call([
            get_path('yalignve/bin/pip'),
            'install',
            'pip',
            '-U'
        ])
        subprocess.call([
            get_path('yalignve/bin/pip'),
            'install',
            '-r',
            'requirements_yalign_1.txt'
        ])
        subprocess.call([
            get_path('yalignve/bin/pip'),
            'install',
            '-r',
            'requirements_yalign_2.txt'
        ])
        subprocess.call([
            get_path('yalignve/bin/pip'),
            'install',
            'yalign==0.1.1'
        ])

    env = dict(os.environ)
    env['PYTHONPATH'] = work_dir
    web_ui_args = [get_path('ve/bin/python'), '-m', 'alignerwebapp.main']
    if conf.debug:
        web_ui_args.append('--debug')
    web_ui = threading.Thread(
        target=subprocess.call,
        args=[web_ui_args],
        kwargs={'env': env},
        daemon=True
    )
    web_ui.start()

    aligner_args = [
        get_path('ve/bin/python'),
        '-m', 'alignworker.main',
        '--yalign-python', get_path('yalignve/bin/python')
    ]
    if conf.debug:
        aligner_args.append('--debug')
    aligner = threading.Thread(
        target=subprocess.call,
        args=[aligner_args],
        kwargs={'env': env},
        daemon=True
    )
    aligner.start()

    web_ui.join()
    aligner.join()

if __name__ == '__main__':
    main()
