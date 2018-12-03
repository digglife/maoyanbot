# -*- coding:utf-8 -*-
import os
from datetime import datetime
import scrapy
from scrapy.utils.project import get_project_settings
import requests

class XiciProxy(scrapy.Spider):
    name = 'proxy'
    # no need to use pipeline or proxy for this spider
    custom_settings = {'ITEM_PIPELINES': {}, 'ROTATING_PROXY_LIST_PATH': None}

    def start_requests(self):
        project_settings = get_project_settings()
        proxy_list = project_settings.get('ROTATING_PROXY_LIST_PATH', 'proxies.txt')
        self.file = open(proxy_list, 'w')
        return [scrapy.Request('http://www.xicidaili.com/nt/1', callback=self.parse)]

    def parse(self, response):
        is_today = True
        table = response.xpath('//table[@id="ip_list"]')
        trs = table.xpath('tr')
        now = datetime.now()
        for tr in trs[1:]:
            tds = [i.xpath('text()').get() for i in tr.xpath('td')]
            #tds = tr.xpath('td/text()')
            validate_datetime = datetime.strptime(tds[-1], '%y-%m-%d %H:%M')
            if (now - validate_datetime).total_seconds() > 86400:
                is_today = False
                break
            ip = tds[1]
            port = tds[2]
            if port == '80':
                continue
            scheme = tds[5].lower()
            proxy_url = '{}://{}:{}'.format(scheme, ip, port)

            self.logger.info("now checking the availability of proxy {}".format(proxy_url))
            # maybe validate the availability for the proxy?
            if self.is_proxy_available(proxy_url):
                self.file.write(proxy_url + '\n')

        if is_today:
            next_page = int(response.url.split('/')[-1]) + 1
            yield response.follow('http://www.xicidaili.com/nt/{}'.format(next_page),
                                  callback=self.parse)

    def closed(self, reason):
        self.file.close()

    @staticmethod
    def is_proxy_available(proxy):
        try:
            res = requests.head('http://www.baidu.com', proxies={'http': proxy}, timeout=3)
            return res.ok
        except:
            return False