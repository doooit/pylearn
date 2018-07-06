# -*- coding: utf-8 -*-
import scrapy
import urlparse

from lexicon_spider.items import SogouDictItem

class SogouSpider(scrapy.Spider):
    name = 'sogou'
    allowed_domains = ['sogou.com']
    start_url_tags = [
       {'tag_name':u'城市信息', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/167'},
       #{'tag_name':u'自然科学', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/1'},
       #{'tag_name':u'社会科学', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/76'},
       #{'tag_name':u'工程应用', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/96'},
       #{'tag_name':u'农林渔畜', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/127'},
       #{'tag_name':u'医学医药', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/132'},
       #{'tag_name':u'电子游戏', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/436'},
       #{'tag_name':u'艺术设计', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/154'},
       #{'tag_name':u'生活百科', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/389'},
       #{'tag_name':u'运动休闲', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/367'},
       #{'tag_name':u'人文科学', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/31'},
       #{'tag_name':u'娱乐休闲', 'tag_url':'https://pinyin.sogou.com/dict/cate/index/403'}
    ]
    #start_urls = [
    #    'https://pinyin.sogou.com/dict/cate/index/366'
    #]

    base_url = 'https://pinyin.sogou.com'

    def start_requests(self):
        for tag_info in self.start_url_tags:
            yield scrapy.Request(tag_info['tag_url'], callback=self.parse, meta={'first_cate_name': tag_info['tag_name']})

    def parse(self, response):
        if response.url == 'https://pinyin.sogou.com/dict/cate/index/167':
            for main_cate_ele in response.xpath('.//*[@id="city_list_show"]/table/tbody/tr/td/div'):
                main_cate_name = main_cate_ele.xpath('.//a/text()').extract()[0]
                main_url = main_cate_ele.xpath('.//a/@href').extract()[0]
                target_url = urlparse.urljoin(self.base_url, main_url)
                yield scrapy.Request(target_url, callback=self.parse_second, meta={'first_cate_name': response.meta['first_cate_name'], 'second_cate_name': main_cate_name})
        else:
            for main_cate_ele in response.xpath('.//*[@id="dict_cate_show"]/table/tbody/tr/td/div[1]'):
                main_cate_name = main_cate_ele.xpath('.//a/text()').extract()[0]
                main_url = main_cate_ele.xpath('.//a/@href').extract()[0]
                has_sub = False
                for sub_cate_ele in main_cate_ele.xpath('.//following-sibling::div/table/tbody/tr/td/div'):
                    has_sub = True
                    sub_cate_name = sub_cate_ele.xpath('.//a/text()').extract()[0]
                    sub_cate_url = sub_cate_ele.xpath('.//a/@href').extract()[0]
                    target_url = urlparse.urljoin(self.base_url, sub_cate_url)
                    yield scrapy.Request(target_url, callback=self.parse_dict_list, meta={'first_cate_name': response.meta['first_cate_name'], 'second_cate_name': main_cate_name, 'third_cate_name': sub_cate_name})
                else:
                    if not has_sub:
                        target_url = urlparse.urljoin(self.base_url, main_url)
                        print(target_url)
                        yield scrapy.Request(target_url, callback=self.parse_dict_list, meta={'first_cate_name': response.meta['first_cate_name'], 'second_cate_name': main_cate_name, 'third_cate_name': ''})

    def parse_second(self, response):
        third_cate = response.xpath('.//*[@id="dict_cate_show"]/table/tbody/tr/td/div[@class="cate_no_child no_select"]')
        if not third_cate:
            yield scrapy.Request(response.url, callback=self.parse_dict_list, meta={'first_cate_name': response.meta['first_cate_name'], 'second_cate_name': response.meta['second_cate_name'], 'third_cate_name': ''}, dont_filter=True)
        else:
            for third_cate_ele in response.xpath('.//*[@id="dict_cate_show"]/table/tbody/tr/td/div[@class="cate_no_child no_select"]'):
                try:
                    third_cate_name = third_cate_ele.xpath('.//a/text()').extract()[0]
                    third_url = third_cate_ele.xpath('.//a/@href').extract()[0]
                except IndexError as exc:
                    pass
                else:
                    target_url = urlparse.urljoin(self.base_url, third_url)
                    yield scrapy.Request(target_url, callback=self.parse_dict_list, meta={'first_cate_name': response.meta['first_cate_name'], 'second_cate_name': response.meta['second_cate_name'], 'third_cate_name': third_cate_name})

    def parse_dict_list(self, response):
        for dict_info in response.xpath('.//div[@class="dict_detail_title_block"]'):
            dict_name = dict_info.xpath('.//div/a/text()').extract()[0]
            download_url = dict_info.xpath('.//following-sibling::div/div/a/@href').extract()[0]
            yield scrapy.Request(download_url, callback=self.download_dict, meta={'first_cate_name': response.meta['first_cate_name'], 'second_cate_name': response.meta['second_cate_name'], 'third_cate_name': response.meta['third_cate_name'], 'dict_name': dict_name})

        for page_a in response.xpath('.//*[@id="dict_page_list"]/ul/li'):
            try:
                page_text = page_a.xpath('.//a/text()').extract()[0]
                page_url = page_a.xpath('.//a/@href').extract()[0]
            except IndexError as exc:
                continue

            if page_text == u'下一页':
                target_url = urlparse.urljoin(self.base_url, page_url)
                yield scrapy.Request(target_url, callback=self.parse_dict_list, meta={'first_cate_name': response.meta['first_cate_name'], 'second_cate_name': response.meta['second_cate_name'], 'third_cate_name': response.meta['third_cate_name']})

    def download_dict(self, response):
        yield SogouDictItem(first_cate_name=response.meta['first_cate_name'], second_cate_name=response.meta['second_cate_name'], third_cate_name=response.meta['third_cate_name'], dict_name=response.meta['dict_name'], dict_body=response.body)

