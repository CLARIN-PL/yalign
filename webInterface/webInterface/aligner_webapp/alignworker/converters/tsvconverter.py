import os
import logging
from alignworker.tmp import get_temp_file

log = logging.getLogger(__name__)

def to_tsv(path1, path2):
    out_path = get_temp_file()
    log.info('Convert to TSV from "%s" + "%s" to "%s"', path1, path2, out_path)
    with open(out_path, 'w') as f:
        with open(path1) as f1, open(path2) as f2:
            for rec1, rec2 in zip(f1, f2):
                rec1 = rec1.replace('\t', ' ')
                rec2 = rec2.replace('\t', ' ')
                f.write(rec1.strip())
                f.write('\t')
                f.write(rec2.strip())
                f.write('\n')
    return out_path
