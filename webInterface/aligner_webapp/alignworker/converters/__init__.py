import os
import logging
import shutil
import subprocess
import tempfile
from alignworker.tmp import get_temp_file
from .tokenizer import tokenize
from .detokenizer import detokenize
from .tmxconverter import to_tmx
from .tsvconverter import to_tsv

log = logging.getLogger(__name__)

def doc_to_plaintext(path):
    """TODO: Docstring for doc_to_plaintext.

    :path: TODO
    :returns: TODO

    """
    out_path = get_temp_file()
    if not(path.endswith('.doc') or path.endswith('.docx') or path.endswith('.odt')):
        shutil.copyfile(path, out_path)
        return out_path
    log.info('Converting doc into text file from "%s" to "%s"', path, out_path)
    tmp_dir = tempfile.mkdtemp(suffix='_doc_to_text_')
    subprocess.call([
        'soffice',
        '--headless',
        '--convert-to',
        'txt:Text',
        '--outdir',
        tmp_dir,
        path
    ])
    try:
        dirpath, _, filenames = next(os.walk(tmp_dir))
        converted_path = os.path.join(dirpath, filenames[0])
        shutil.copyfile(converted_path, out_path)
        shutil.rmtree(tmp_dir)
    except IndexError:
        shutil.copyfile(path, out_path)
    return out_path

def norm_utf8(path):
    """TODO: Docstring for norm_utf8.

    :path: TODO
    :returns: TODO

    """
    out_path = get_temp_file()
    with open(out_path, 'w', encoding='utf-8') as f:
        with open(path, encoding='utf-8', errors='replace') as in_f:
            for rec in in_f:
                f.write(rec)
    return out_path
