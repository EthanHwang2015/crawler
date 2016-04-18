#encoding=utf8
import scrapy
import os
class CrawlBaidu(scrapy.spiders.Spider):
    name = 'baidu'
    start_urls = ["http://www.baidu.com"]
    def parse(self, response):
        pageStep = 10 
        maxIndex = 3
        searchPattern = '/s?wd='
        wordList = []
        with open('zhichangai_symp.txt', 'r') as f:
            for line in f.readlines():
                wordList.append(line.strip())
        for word in wordList:
            url = response.url + searchPattern + word
            for i in xrange(maxIndex):
                pn = i*pageStep
                yield scrapy.Request(url + '&pn=' + str(pn), callback=self.actualParse, meta={'pn':str(i), 'word':word})
    def actualParse(self, response):
        path = 'output/'
        if not os.path.exists(path):
            os.mkdir(path)
        outputName = path + response.meta['word'] + "_" + response.meta['pn']
        with open(outputName, 'w') as f:
            f.write(response.body)
        
