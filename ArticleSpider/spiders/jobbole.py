# -*- coding: utf-8 -*-
import scrapy
import re
from urllib import parse
from ArticleSpider.items import JobBoleAricleItem, ArticleItemLoader
from scrapy.http import Request
from ArticleSpider.utils.common import get_md5
import datetime
from scrapy.loader import ItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        # 获取当前页面所有文章的url
        post_nodes = response.css('#archive .floated-thumb .post-thumb a')
        for post_node in post_nodes:
            # 初始化Request,有时候post_url可能不是完整的url
            # 我们这里是，http://blog.jobbole.com/114706/，有时候可能是114706
            # 这里是用以下方法得到拼接的url
            # Request(url=post_url, callback=self.parse_detail())
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_img_url": image_url},
                          callback=self.parse_detail)
            # 提取下一页
        next_url = response.css('.next.page-numbers ::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, post_url), callback=self.parse)

    def parse_detail(self, response):
        article_item = JobBoleAricleItem()
        # 使用css提取文章具体字段
        title = response.css('.entry-header h1::text').extract()[0]
        create_date = response.css('.entry-meta-hide-on-mobile::text').extract()[0].strip().split(' ')[0]
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d")
        except Exception as e:
            create_date = datetime.datetime.now().date()
        # response.xpath('//span[contains(@class,"vote-post-up")]/h10/text()').extract()
        praise_nums = response.css('.vote-post-up h10 ::text').extract()[0]
        image_url = response.css("img::attr(src)").extract_first("")
        front_img_url = response.meta.get("front_img_url", "")
        fav_nums = response.css('.bookmark-btn::text').extract()[0]
        pattern = '.*?(\d+).*$'
        match_re = re.match(pattern, fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0
        content = response.xpath('//div[@class="entry"]').extract_first()
        tar_list = response.css('p.entry-meta-hide-on-mobile>a::text').extract()
        tags = [element for element in tar_list if not element.strip().endswith('评论')]
        article_item["title"] = title
        article_item["url"] = response.url
        article_item["create_date"] = create_date
        article_item["praise_nums"] = praise_nums
        article_item["front_img_url"] = [front_img_url]
        article_item["content"] = content
        article_item["tags"] = tags
        article_item["fav_nums"] = fav_nums
        article_item["url_object_id"] = get_md5(response.url)

        # 通过itemloaader 加载item
        item_loader = ArticleItemLoader(item=JobBoleAricleItem(), response=response)
        # item_loader = ArticleItemLoader(item=JobBoleAricleItem(), response=response)
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_img_url", [front_img_url])
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")
        article_item = item_loader.load_item()
        yield article_item
