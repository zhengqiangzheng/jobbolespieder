# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join
import datetime
import re


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def date_convert(value):
    try:
        create_date = datetime.datetime.strptime(value, "%Y%m%d").date()
    except Exception as e:
        create_date = datetime.datetime.now().date()
    return create_date


def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = match_re.group(1)
    else:
        nums = 0
    return nums


def remove_comment_tags(value):
    if "评论" in value:
        return ""
    else:
        return value


def return_value(value):
    return value


class JobBoleAricleItem(scrapy.Item):
    title = scrapy.Field(
        input_processor=MapCompose(lambda x: x + "-zq")
    )
    create_date = scrapy.Field(
        input_processor=MapCompose(date_convert),
        # output_processor=TakeFirst()
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)

    )
    content = scrapy.Field()
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
        output_processor=Join(",")

    )
    front_img_url = scrapy.Field(
        output_processor=MapCompose(return_value)

    )
    front_image_path = scrapy.Field()


class ArticleItemLoader(ItemLoader):
    default_output_processor = TakeFirst()
