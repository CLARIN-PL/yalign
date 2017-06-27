# -*- coding: utf-8 -*-
"""
Description: 
"""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function

import os
import logging
import re
import codecs
from argparse import ArgumentParser
from yalign import YalignModel, text_to_document

_readme = """
"""
_readme = _readme.strip()

logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
log = logging.getLogger('yalign')

def get_conf():
    parser = ArgumentParser(description='Yalign aligner script', usage=_readme)
    parser.add_argument('models', help='Path to models')
    parser.add_argument('model', help='Model to use for aligning')
    parser.add_argument('in1', type=os.path.abspath, help='First input file for aligning')
    parser.add_argument('in2', type=os.path.abspath, help='Second input file for aligning')
    parser.add_argument('out1', type=os.path.abspath, help='Output of first aligned file')
    parser.add_argument('out2', type=os.path.abspath, help='Output of second aligned file')
    return parser.parse_args()

re_win_newline = re.compile(u'\r\n', re.MULTILINE)
re_extra_space = re.compile(ur'\s{2,}')
def remove_extra_spaces(text):
    """@todo: Docstring for remove_extra_spaces.

    :text: @todo
    :returns: @todo

    """
    text = re_win_newline.sub(u'\n', text)
    text = (t for t in text.split(u'\n'))
    text = (t.strip() for t in text)
    text = (re_extra_space.sub(' ', t) for t in text)
    text = (t for t in text if len(t) >= 2)
    return '\n'.join(text)

def main():
    conf = get_conf()
    os.chdir(conf.models)

    with codecs.open(conf.in1, encoding='utf-8') as f:
        in1 = f.read()
    with codecs.open(conf.in2, encoding='utf-8') as f:
        in2 = f.read()
    doc1 = text_to_document(remove_extra_spaces(in1))
    doc2 = text_to_document(remove_extra_spaces(in2))
    model = YalignModel.load(conf.model)
    pairs = model.align(doc1, doc2)
    pairs = [(p[0].to_text(), p[1].to_text()) for p in pairs]
    text1 = [p[0] for p in pairs]
    text1 = [t+'\n' for t in text1]
    text1 = ''.join(text1)
    text2 = [p[1] for p in pairs]
    text2 = [t+'\n' for t in text2]
    text2 = ''.join(text2)
    with open(conf.out1, 'wb') as f:
        f.write(text1)
    with open(conf.out2, 'wb') as f:
        f.write(text2)

if __name__ == '__main__':
    main()
