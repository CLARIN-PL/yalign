import os
import tempfile
import functools
import subprocess


def align_fab(hunalign_path):
    """TODO: Docstring for align_fab.

    :hunalign_path: TODO
    :returns: TODO

    """
    return functools.partial(align, hunalign_path)

def align(hunalign_path, lang1, lang2, path1, path2):
    h1, out_path1 = tempfile.mkstemp()
    h2, out_path2 = tempfile.mkstemp()
    os.close(h1)
    os.close(h2)
    with open(out_path1, 'w') as out1, open(out_path2, 'w') as out2:
        text1, text2 = parts_align(hunalign_path, path1, path2)
        out1.write(text1)
        out2.write(text2)
    return out_path1, out_path2

def hunalign_align(hunalign, path1, path2):
    result = subprocess.check_output([
        hunalign,
        '-text',
        '-utf',
        '/dev/null',
        path1,
        path2
    ])
    sentences = []
    result = result.decode('utf-8')
    for rec in result.split('\n'):
        tokens = rec.split('\t')
        if len(tokens) == 3:
            sentences.append((tokens[0], tokens[1]))
    # no need to save empty file
    if not sentences:
        return '', ''
    # filter and strip
    sentences = [
        (s1.strip(u'\t\n\r\f\v \ufeff'),
            s2.strip(u'\t\n\r\f\v \ufeff'))
        for s1, s2 in sentences
    ]
    sentences = [(s1, s2) for s1, s2 in sentences
                    if s1 and s2 and not s1 == s2]
    text1 = u'\n'.join(s1 for s1, _ in sentences)
    text2 = u'\n'.join(s2 for _, s2 in sentences)
    return text1, text2

def parts_align(hunalign, path1, path2):
    text1 = ''
    text2 = ''
    fd1, temp_path1 = tempfile.mkstemp()
    fd2, temp_path2 = tempfile.mkstemp()
    os.close(fd1)
    os.close(fd2)
    size1 = 0
    size2 = 0
    with open(path1) as f1, open(path2) as f2:
        with open(temp_path1, 'wb', 0) as tf1, open(temp_path2, 'wb', 0) as tf2:
            size1 = 0
            size2 = 0
            for rec1, rec2 in zip(f1, f2):
                size1 += len(rec1)
                size2 += len(rec2)
                tf1.write(rec1.encode('utf-8'))
                tf2.write(rec2.encode('utf-8'))
                if size1 > 1048576 or size2 > 1048576:
                    next_text1, next_text2 = hunalign_align(hunalign, temp_path1, temp_path2)
                    text1 += next_text1
                    text2 += next_text2
                    size1 = size2 = 0
                    tf1.seek(0)
                    tf1.truncate()
                    tf2.seek(0)
                    tf2.truncate()
            if size1 and size2:
                next_text1, next_text2 = hunalign_align(hunalign, temp_path1, temp_path2)
                text1 += next_text1
                text2 += next_text2
        os.unlink(temp_path1)
        os.unlink(temp_path2)
    return text1, text2
