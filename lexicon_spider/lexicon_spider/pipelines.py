# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import os
import requests

def assure_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)

class LexiconSpiderPipeline(object):
    def process_item(self, item, spider):
        dict_path = os.path.join('.', item['main_cate_name'], item['sub_cate_name'])
        dict_file = os.path.join('.', item['main_cate_name'], item['sub_cate_name'], '%s.scel'%item['dict_name'])
        assure_exists(dict_path)
        ret = requests.get(item['download_url'])
        if str(ret.status_code) == '200':
            with open(dict_file, 'wb') as fp:
                fp.write(ret.content)
        return item
