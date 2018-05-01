#!/usr/bin/env python
"""
@file trip_info.py


This to read tripinfo.xml and find the features of simulation
"""

import pandas as pd
import xml.etree.cElementTree as et


def iter_docs(author):
    author_attr = author.attrib
    print(author_attr)
    for doc in author.iter('tripinfos'):
        doc_dict = author_attr.copy()
        doc_dict.update(doc.attrib)
        doc_dict['tripinfo'] = doc.text
        yield doc_dict


def iter_author(etree):
    for author in etree.iter('author'):
        for row in iter_docs(author):
            yield row

parsed_xml = et.parse("tripinfo.xml")

for doc in parsed_xml.iter('tripinfos'):
    for d in doc.iter('tripinfo'):
        print(d)

# print(parsed_xml.getroot())
# doc_df = pd.DataFrame(list(iter_docs(parsed_xml.getroot())))
# print(doc_df)
