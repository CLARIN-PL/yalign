import os
import shutil
import time
import json
import tempfile
import random
import zipfile
import logging
from datetime import datetime
from alignworker import aligners
from alignworker import converters

def convert_pair(converter, path1, path2, delete_original=True):
    new_path1 = converter(path1)
    new_path2 = converter(path2)
    if delete_original:
        os.unlink(path1)
        os.unlink(path2)
    return new_path1, new_path2

class AlignerWorker(object):

    """Docstring for AlignerWorker. """

    log = logging.getLogger(__name__)

    def __init__(self, workq, hunalign_path, yalign_python, yalign_script, models):
        """TODO: to be defined1. """

        self.workq = workq
        self.aligners = {
            'hunalign': aligners.hunalign.align_fab(hunalign_path),
            'yalign': aligners.yalign.align_fab(yalign_python, yalign_script, models)
        }

    def start(self):
        """TODO: Docstring for start.
        :returns: TODO

        """
        while True:
            next_task = self.workq.start_next_task()
            if next_task:
                self.log.info('New align task: %s', next_task['id'])
                self.process(next_task)
                self.log.info('Task ready: %s', next_task['id'])
            time.sleep(10)

    def get_result_paths(self, result_dir, lang1, lang2, name1, name2):
        """TODO: Docstring for get_result_paths.

        :result_dir: TODO
        :lang1: TODO
        :lang2: TODO
        :name1: TODO
        :name2: TODO
        :returns: TODO

        """
        result1 = os.path.join(result_dir, '{}-{}.txt'.format(lang1, name1))
        result2 = os.path.join(result_dir, '{}-{}.txt'.format(lang2, name2))
        if not os.path.exists(result1) and not os.path.exists(result2):
            return result1, result2
        while True:
            random_name = str(random.randint(0, 1000))
            result1 = os.path.join(result_dir, '{}-{}-{}.txt'.format(lang1, random_name, name1))
            result2 = os.path.join(result_dir, '{}-{}-{}.txt'.format(lang2, random_name, name2))
            if not os.path.exists(result1) and not os.path.exists(result2):
                return result1, result2

    def get_result_path(self, result_dir, lang1, lang2, name, ext):
        """TODO: Docstring for get_result_path.

        :result_dir: TODO
        :lang1: TODO
        :lang2: TODO
        :name: TODO
        :ext: TODO
        :returns: TODO

        """
        result = os.path.join(result_dir, '{}-{}-{}.{}'.format(lang1, lang2, name, ext))
        if not os.path.exists(result):
            return result
        while True:
            random_name = str(random.randint(0, 1000))
            result = os.path.join(result_dir, '{}-{}-{}-{}.{}'.format(lang1, lang2, name, random_name, ext))
            if not os.path.exists(result):
                return result

    def process(self, task):
        """TODO: Docstring for process.

        :task: TODO
        :returns: TODO

        """
        data = json.loads(task['data'])
        method = data['method']
        lang1 = data['lang1']
        lang2 = data['lang2']
        output = data['output']
        self.log.info('Processing with method "%s", languages "%s-%s", output "%s"', method, lang1, lang2, output)
        temp_path = tempfile.mkdtemp(prefix='tmp_aligner_')
        result_name = 'aligned_files_{}-{}_{}'.format(
            lang1,
            lang2,
            datetime.utcnow().strftime('%d-%m-%Y_%H%M')
        )
        result_path = os.path.join(
            temp_path,
            result_name
        )
        os.mkdir(result_path)
        for pair in self.workq.iter_input_pairs(task['id']):
            self.log.info('Processing file pair: %s', pair)
            path1 = pair[lang1]
            path2 = pair[lang2]
            name1 = os.path.basename(path1)
            # for name2 using same name1 to keep similar names for aligned texts
            name2 = name1

            # prepare input files
            path1, path2 = convert_pair(
                converters.doc_to_plaintext,
                path1,
                path2,
                delete_original=False
            )
            path1, path2 = convert_pair(
                converters.norm_utf8,
                path1,
                path2
            )

            #

            if method == 'hunalign':

                # tokeninze
                path1, path2 = convert_pair(
                    converters.tokenize,
                    path1,
                    path2,
                )

                # align
                result1, result2 = self.aligners['hunalign'](lang1, lang2, path1, path2)
                os.unlink(path1)
                os.unlink(path2)
                path1, path2 = result1, result2

                # detokenize
                result1, result2 = convert_pair(
                    converters.detokenize,
                    path1,
                    path2
                )
            elif method == 'yalign':
                result1, result2 = self.aligners['yalign'](lang1, lang2, path1, path2)
            else:
                raise RuntimeError('Unknown aligner name')

            if output == 'plaintext':
                save_path1, save_path2 = self.get_result_paths(result_path, lang1, lang2, name1, name2)
                shutil.move(result1, save_path1)
                shutil.move(result2, save_path2)
            elif output == 'tmx':
                save_path = self.get_result_path(result_path, lang1, lang2, name1, 'tmx')
                result = converters.to_tmx(lang1, lang2, result1, result2)
                shutil.move(result, save_path)
                os.unlink(result1)
                os.unlink(result2)
            elif output == 'tsv':
                save_path = self.get_result_path(result_path, lang1, lang2, name1, 'tsv')
                result = converters.to_tsv(result1, result2)
                shutil.move(result, save_path)
                os.unlink(result1)
                os.unlink(result2)
            else:
                raise RuntimeError('Unknown output format')
        os.chdir(temp_path)
        zip_path = os.path.join(temp_path, result_name + '.zip')
        with zipfile.ZipFile(zip_path, 'w') as z:
            for file_name in os.listdir(result_path):
                next_path = os.path.join(result_name, file_name)
                z.write(next_path)
        self.workq.complete_task_with_result(task['id'], zip_path)
        shutil.rmtree(temp_path)
