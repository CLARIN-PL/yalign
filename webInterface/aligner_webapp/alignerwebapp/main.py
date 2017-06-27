import os
import logging
from argparse import ArgumentParser
from workq import db
from alignerwebapp.webapp import app

_readme = """
"""
_readme = _readme.strip()

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
log = logging.getLogger(__name__)

def get_conf():
    parser = ArgumentParser(description='', usage=_readme)
    parser.add_argument('--work-db', type=os.path.abspath, default='work.db', help='Path to database with work status')
    parser.add_argument('--models', type=os.path.abspath, default='models', help='Path to Yalign aligning models')
    parser.add_argument('--data', type=os.path.abspath, default='_data', help='Path to data files related to work')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    return parser.parse_args()

def main():
    conf = get_conf()
    log.info('Work DB path: %s', conf.work_db)
    log.info('Models path: %s', conf.models)
    log.info('Data path: %s', conf.data)
    app.config.update(
        work_db=conf.work_db,
        yalign_models=conf.models,
        data_path=conf.data
    )
    app.run(host='0.0.0.0', port=9000, debug=conf.debug)

if __name__ == '__main__':
    main()
