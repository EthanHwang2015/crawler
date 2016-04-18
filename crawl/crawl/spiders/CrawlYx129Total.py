#encoding=utf8
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
import os

class CrawlYx129Total(CrawlSpider):
    name = 'yx129_total'
    allowed_domains = ['yx129.com']
    start_urls = ['http://www.yx129.com']
    prefix = 'http://www.yx129.com'
    #start_urls = ['http://www.yx129.com']

    headers = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip,deflate",
        "Accept-Language": "en-US,en;q=0.8,zh-TW;q=0.6,zh;q=0.4",
        "Connection": "keep-alive",
        "Content-Type":" application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36",
        "Referer": "http://www.yx129.com/"
    }

    #don't overide parse function when use rules !!!!!!

    def start_requests(self):
        loginUrl = 'http://www.yx129.com/login.php?task=UserLogin'
        return [scrapy.FormRequest(loginUrl,
            meta = {'cookiejar':1},
            headers = self.headers,
            formdata = {
                'check':'true',
                'email':'18611562835',
                'password':'123456ab' 
            },
            callback = self.afterLogin)]

    def afterLogin(self, response):
        #print response.body
        maxPage = 70000
        searchUrl = 'http://www.yx129.com/bingli/1_%s.html'
        for i in xrange(maxPage):
            yield scrapy.Request(searchUrl %(str(i)), meta = {'cookiejar':1}, callback=self.parseHtml)
        #print searchUrl
        #for url in self.start_urls:
        #    yield self.make_requests_from_url(url)

    '''
    def parse(self, response):
        print response.url

    '''
    def parsePage(self, response):
        print response.url
        sel = Selector(response)
        urls = sel.xpath('//a[@class="highlight"]/@href').extract()
        for url in urls:
            url = self.prefix + url
            yield scrapy.Request(url, meta = {'cookiejar':1}, callback=self.parseHtml)


    def parseHtml(self, response):
        detail = 'http://yx129.com/components/illness/case_detail_search.php?action=showwenku'
        sel = Selector(response)
        uid = sel.xpath('//div[@class="avatarBox"]/a/@href').extract()
        if len(uid) > 0:
            bingli = response.url.split('.html')[0].split('_')[-1]
            url = detail + '&blAccId=' + uid[0].split('uid=')[-1] + '&bl_id=' +  bingli
            yield scrapy.Request(url, meta = {'cookiejar':1, 'fileName':bingli}, callback = self.downLoad)

    def downLoad(self, response):
        path = 'output/'
        if not os.path.exists(path):
            os.mkdir(path)

        fileName = path + response.meta['fileName'] + '.swf'
        with open(fileName, 'w') as f:
            f.write(response.body)
