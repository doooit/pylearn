# -*- coding: utf-8 -*-
import scrapy
import urlparse

from lexicon_spider.items import DictItem

class SogouSpider(scrapy.Spider):
    name = 'sogou'
    allowed_domains = ['sogou.com']
    start_urls = ['https://pinyin.sogou.com/dict/cate/index/436']
    #start_urls = ['https://pinyin.sogou.com/dict/cate/index/612']
    base_url = 'https://pinyin.sogou.com'

    def parse(self, response):
        for main_cate_ele in response.xpath('.//*[@id="dict_cate_show"]/table/tbody/tr/td/div[1]'):
            main_cate_name = main_cate_ele.xpath('.//a/text()').extract()[0]
            for sub_cate_ele in main_cate_ele.xpath('.//following-sibling::div/table/tbody/tr/td/div'):
                sub_cate_name = sub_cate_ele.xpath('.//a/text()').extract()[0]
                sub_cate_url = sub_cate_ele.xpath('.//a/@href').extract()[0]
                target_url = urlparse.urljoin(self.base_url, sub_cate_url)
                yield scrapy.Request(target_url, callback=self.parse_dict_list, meta={'main_cate_name': main_cate_name, 'sub_cate_name': sub_cate_name})

    def parse_dict_list(self, response):
        for dict_info in response.xpath('.//div[@class="dict_detail_title_block"]'):
            dict_name = dict_info.xpath('.//div/a/text()').extract()[0]
            download_url = dict_info.xpath('.//following-sibling::div/div/a/@href').extract()[0]
            yield {'main_cate_name': response.meta['main_cate_name'], 'sub_cate_name': response.meta['sub_cate_name'], 'dict_name': dict_name, 'download_url': download_url}
            yield scrapy.Request(download_url, callback=self.download_dict, meta={'main_cate_name': response.meta['main_cate_name'], 'sub_cate_name': response.meta['sub_cate_name'], 'dict_name': dict_name})

        for page_a in response.xpath('.//*[@id="dict_page_list"]/ul/li'):
            try:
                page_text = page_a.xpath('.//a/text()').extract()[0]
                page_url = page_a.xpath('.//a/@href').extract()[0]
            except IndexError as exc:
                continue

            if page_text == u'下一页':
                target_url = urlparse.urljoin(self.base_url, page_url)
                yield scrapy.Request(target_url, callback=self.parse_dict_list, meta={'main_cate_name': response.meta['main_cate_name'], 'sub_cate_name': response.meta['sub_cate_name']})

    def download_dict(self, response):
        yield DictItem(main_cate_name=response.meta['main_cate_name'], sub_cate_name=response.meta['sub_cate_name'], dict_name=response.meta['dict_name'], dict_body=response.body)
