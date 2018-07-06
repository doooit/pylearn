# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SogouDictItem(scrapy.Item):
    # define the fields for your item here like:
    first_cate_name = scrapy.Field()
    second_cate_name = scrapy.Field()
    third_cate_name = scrapy.Field()
    dict_name = scrapy.Field()
    dict_body = scrapy.Field()

