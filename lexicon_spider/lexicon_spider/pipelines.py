# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import re
import requests

from lexicon_spider.items import SogouDictItem

def assure_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

class LexiconSpiderPipeline(object):
    def process_item(self, item, spider):
        if isinstance(item, SogouDictItem):
            file_name = re.sub('[\/:*?"<>|]','-', item['dict_name'])
            dict_path = os.path.join('.', 'SogouDict', item['first_cate_name'], item['second_cate_name'], item['third_cate_name'])
            dict_file = os.path.join('.', 'SogouDict', item['first_cate_name'], item['second_cate_name'], item['third_cate_name'], '%s.scel'%file_name)
            assure_exists(dict_path)
            with open(dict_file, 'wb') as fp:
                fp.write(item['dict_body'])
        return item
