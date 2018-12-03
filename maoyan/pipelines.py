# -*- coding: utf-8 -*-

import os
from scrapy.exporters import JsonLinesItemExporter


class MaoyanPipeline(object):

    def __init__(self, **kwargs):
        self.files = {}

    def open_spider(self, spider):
        file = open('{}.jsonline'.format(spider.name), 'wb')
        self.files[spider.name] = file
        self.exporter = JsonLinesItemExporter(file, encoding='utf8', sort_keys=True)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        file = self.files.pop(spider.name)
        file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
