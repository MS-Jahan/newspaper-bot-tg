import os
import chardet
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

# with open(os.path.join(__location__, 'saved_urls.txt'), 'r', encoding='utf8') as my_file:
#     prev_slugs = my_file.readlines()

# fileObject = open(os.path.join(__location__, 'saved_urls.txt'), "r", encoding='utf8')

# # print(prev_slugs)

# detect = chardet.detect(fileObject.read())
# print(detect)

import codecs
with codecs.open(os.path.join(__location__, 'saved_urls.txt'), 'r', 'utf8' ) as ff:
    content = ff.read().splitlines()

print(content)