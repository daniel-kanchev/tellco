import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from tellco.items import Article


class TellcoSpider(scrapy.Spider):
    name = 'tellco'
    start_urls = ['https://www.tellco.ch/en/Blog']

    def parse(self, response):
        links = response.xpath('//div[@class="ReadMore"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_pages = response.xpath('//ul[@class="Pagination"]//a/@href').getall()
        yield from response.follow_all(next_pages, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//div[@class="BlogDate"]/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//div[@id="BlogContent"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
