import os
import tempfile
import functools
import subprocess

def align_fab(python_bin, yalign_script, model_path):
    return functools.partial(align, python_bin, yalign_script, model_path)

def align(python_bin, yalign_script, model_path, lang1, lang2, path1, path2):
    h1, out_path1 = tempfile.mkstemp()
    h2, out_path2 = tempfile.mkstemp()
    os.close(h1)
    os.close(h2)
    model = '{}-{}'.format(lang1, lang2)
    subprocess.call([
        python_bin,
        yalign_script,
        model_path,
        model,
        path1,
        path2,
        out_path1,
        out_path2
    ])
    return out_path1, out_path2
