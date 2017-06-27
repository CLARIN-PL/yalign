import os
import tempfile


def align(lang1, lang2, path1, path2):
    h1, out_path1 = tempfile.mkstemp()
    h2, out_path2 = tempfile.mkstemp()
    os.close(h1)
    os.close(h2)
    with open(path1) as f1, open(path2) as f2:
        with open(out_path1, 'w') as out1, open(out_path2, 'w') as out2:
            for rec1, rec2 in zip(f1, f2):
                out1.write(rec1)
                out2.write(rec2)
    return out_path1, out_path2
