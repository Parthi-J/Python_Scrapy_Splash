# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import pymongo
import json
import os
import hashlib
from urllib.parse import quote
from scrapy.exceptions import DropItem

from myscrapy import settings


class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['url'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['url'])
            return item


class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item


class MongoPipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item


class ScreenShotPipeline(object):
    """Pipeline that uses Splash to render screen shot of every Scrapy item."""

    SPLASH_URL = "{}/render.png?url={}"
    # "http://192.168.9.46:8050"
    def process_item(self, item, spider):
        encoded_item_url = quote(item["url"])
        screen_shot_url = self.SPLASH_URL.format(settings.SPLASH_URL, encoded_item_url)

        request = scrapy.Request(screen_shot_url)

        dfd = spider.crawler.engine.download(request, spider)
        dfd.addBoth(self.return_item, item)

        return dfd

    def return_item(self, response, item):
        if response.status != 200:
            return item

        # Save screen shot to file, filename will be hash of url.
        here = os.path.dirname(os.path.realpath(__file__))
        subdir = os.path.join(here, "Screenshots")

        # create subdirectory
        if not os.path.isdir(subdir):
            os.mkdir(subdir)

        url = item["url"]
        url_hash = hashlib.md5(url.encode("utf8")).hexdigest()
        filename = "{}.png".format(url_hash)
        file_path = os.path.join(here, subdir, filename)

        try:
            with open(file_path, "wb") as f:
                f.write(response.body)
        except IOError:
            raise DropItem("Wrong path provided")

        # Store filename in item.
        item["screen_shot_filename"] = filename
        return item


class ItemPipeline(object):

    def process_item(self, item, spider):
        if not settings.LOG_ENABLED:
            print(item)

        return item
