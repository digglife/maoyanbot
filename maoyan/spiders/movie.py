# -*- coding: utf-8 -*-
import io
import re

import scrapy
import requests
from maoyan.font import MaoyanFontParser

class MovieSpider(scrapy.Spider):

    name = 'movie'
    allowed_domains = ['maoyan.com']
    offset = 0
    url_template = 'http://maoyan.com/films?showType=3&offset={}'
    start_urls = [url_template.format(0)]
    parser = MaoyanFontParser()

    def parse(self, response):
        movie_urls = response.css('div.movie-item > a::attr(href)').extract()
        if movie_urls:
            for movie in response.css('div.movie-item > a::attr(href)').extract():
                yield response.follow(movie, callback=self.parse_movie, priority=200)
            self.offset += 30
            yield response.follow(self.url_template.format(self.offset), callback=self.parse, priority=100)

    def parse_movie(self, response):
        title_tag = response.css('title::text').get()
        title = title_tag.split('-')[0].strip()

        match = re.search(r'url\(\'(.*\.woff)\'\)', response.text)
        font_url = response.urljoin(match.group(1))
        font = self.parser.load(font_url)

        movie_status = response.css('div.movie-stats-container')

        raw_score = movie_status.css('span.info-num span::text').extract_first()
        if raw_score and '.' in raw_score:
            score = font.transcodes(raw_score)
        else:
            score = None


        box_unit = movie_status.css('div.box span.unit::text').extract_first()
        if box_unit:
            raw_box = movie_status.css('div.box span::text').extract_first()
            box_num = font.transcodes(raw_box)
            box = box_num + box_unit
        else:
            box = None

        movie = {
            'title': title,
            'score': score,
            'box': box,
            'url': response.url
        }

        return movie
