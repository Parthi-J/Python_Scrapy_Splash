import scrapy
from scrapy_splash import SplashRequest
from myscrapy.items import ScrapySplashItem


class ScrapySplash(scrapy.Spider):

    name = "scrapy"

    def __init__(self, **kwargs):
        self.allowed_domains = ['reddit.com']
        self.start_urls = [
            'https://www.reddit.com/'
        ]
        super().__init__(**kwargs)

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url=url, callback=self.parse, endpoint='render.html', args={'wait': 0.5})

    def parse(self, response):
        item = ScrapySplashItem()
        item['url'] = response.url
        item['title'] = response.css('title::text').get()
        yield item

        for a in response.xpath('//a[contains(@href, "/r/")]/@href').extract()[:2]:
            yield response.follow(a, callback=self.parse)
