import os
import logging
import subprocess
from alignworker.tmp import get_temp_file


log = logging.getLogger(__name__)

detokenizer_script = os.path.join(os.path.dirname(__file__), 'detokenizer.perl')

def detokenize(path):
    log.info('Detokenizing file %s', path)
    with open(path, 'rb') as f:
        detokenized_data = subprocess.check_output([
            'perl',
            detokenizer_script
        ], input=f.read())
    out_path = get_temp_file()
    with open(out_path, 'wb') as f:
        f.write(detokenized_data)
    return out_path
