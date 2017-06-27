import os
import logging
from lxml import etree
from alignworker.tmp import get_temp_file


log = logging.getLogger(__name__)

def valide_xml_unicode_char(c):
    codepoint = ord(c)
    return (
        0x20 <= codepoint <= 0xD7FF or
        codepoint in (0x9, 0xA, 0xD) or
        0xE000 <= codepoint <= 0xFFFD or
        0x10000 <= codepoint <= 0x10FFFF
    )

def convert_to_valid_xml_unicode(s):
    s = [c for c in s if valide_xml_unicode_char(c)]
    return ''.join(s)

def to_tmx(lang1, lang2, path1, path2):
    out_path = get_temp_file()
    log.info('Convert to TMX from "%s" + "%s" to "%s"', path1, path2, out_path)

    # Build TMX file
    tmx = etree.Element('tmx', version='1.4')
    tmx.append(etree.Element(
        'header',
        datatype='PlainText',
        segtype='sentence',
        adminlang='{}-{}'.format(lang1, lang2)
    ))
    body = etree.Element('body')
    tmx.append(body)
    with open(path1) as f1, open(path2) as f2:
        for rec1, rec2 in zip(f1, f2):
            tu = etree.Element('tu')
            body.append(tu)

            tuv1 = etree.Element('tuv')
            tu.append(tuv1)
            tuv1.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = lang1
            seg = etree.Element('seg')
            tuv1.append(seg)
            seg.text = convert_to_valid_xml_unicode(rec1.strip())

            tuv2 = etree.Element('tuv')
            tu.append(tuv2)
            tuv2.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = lang2
            seg = etree.Element('seg')
            tuv2.append(seg)
            seg.text = convert_to_valid_xml_unicode(rec2.strip())

    with open(out_path, 'wb') as f:
        f.write(etree.tostring(tmx, pretty_print=True, xml_declaration=True, encoding='utf-8'))
    return out_path
