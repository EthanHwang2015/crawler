#encoding=utf8
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
import os
class BBCSpider(CrawlSpider):
    name = "fuck"
    allowed_domains = ["yx129.com"]
    start_urls = [
        "http://www.yx129.com",
    ]

    rules = [
        Rule(LinkExtractor(allow=r"html"),
             callback='parseItem', follow=True)
    ]


    def parseItem(self, response):
        print(response.url) 
