import logging
import itertools
import nltk.data
from nltk.tokenize.regexp import WordPunctTokenizer
from alignworker.tmp import get_temp_file


log = logging.getLogger(__name__)
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
tokenizer = WordPunctTokenizer()

def tokenize(path):
    log.info('Tokenizing file %s', path)
    # 1. each new line is sentence
    with open(path) as f:
        recs = list(f)
    recs = (r.strip() for r in recs)
    # 2. split sentences inside each new line
    recs = (sent_detector.tokenize(r) for r in recs)
    recs = itertools.chain.from_iterable(recs)
    # 3. tokenize each sentence skipping empty one
    recs = (tokenizer.tokenize(r) for r in recs if r)
    # 4. save file
    out_path = get_temp_file()
    with open(out_path, 'w') as f:
        for rec in recs:
            if rec:
                rec = (r for r in rec if r)
                f.write(' '.join(rec))
                f.write('\n')
    return out_path
