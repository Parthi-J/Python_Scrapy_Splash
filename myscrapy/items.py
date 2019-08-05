# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MyscrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ScrapySplashItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    screen_shot_filename = scrapy.Field()
    last_updated = scrapy.Field(serializer=str)