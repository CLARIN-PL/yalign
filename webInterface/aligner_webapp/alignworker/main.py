import logging
import os
from argparse import ArgumentParser
from alignworker.alignerworker import AlignerWorker
from workq.workq import WorkQ

_readme = """
"""
_readme = _readme.strip()

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
log = logging.getLogger('alignworker')

def get_conf():
    parser = ArgumentParser(description='', usage=_readme)
    parser.add_argument('--work-db', type=os.path.abspath, default='work.db', help='Path to database with work status')
    parser.add_argument('--yalign-python', type=os.path.abspath, help='Python virtualenv for yalign script')
    parser.add_argument('--models', type=os.path.abspath, default='models', help='Path to yalign models')
    parser.add_argument('--data', type=os.path.abspath, default='_data', help='Path to data files related to work')
    parser.add_argument('--debug', action='store_true', help='Debug mode')
    return parser.parse_args()

def main():
    conf = get_conf()
    if conf.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    bin_path = os.path.abspath(os.path.dirname(__file__))
    bin_path = os.path.dirname(bin_path)
    bin_path = os.path.join(bin_path, 'bin')
    hunalign_path = os.path.join(bin_path, 'hunalign')
    yalign_path = os.path.join(bin_path, 'yalign-aligner.py')
    workq = WorkQ(conf.work_db, conf.data)
    aligner = AlignerWorker(workq, hunalign_path, conf.yalign_python, yalign_path, conf.models)
    log.info('Starting aligner')
    aligner.start()

if __name__ == '__main__':
    main()
