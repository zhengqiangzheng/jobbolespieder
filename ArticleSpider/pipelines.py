# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


# 自定义pipeline获得图片名
class ArticleImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value['path']
        item['front_image_path'] = image_file_path
        return item


# 自定义pipeline写入json文件
class JsonWithEncodingPineLine(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        ## json.dumps 将dict转化为字符串
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_close(self, spider):
        self.file.close()


## scrapy自带的
class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open('articleExporter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def open_spider(self, spider):
        print("start")

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect("localhost", "root", "123456", "article_spider", charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
        insert into article(title,create_date,url,url_object_id,praise_nums,content,fav_nums,front_img_url)
        values (%s,%s,%s,%s,%s,%s,%s,%s)
        """
        self.cursor.execute(insert_sql, (
            item["title"], item["create_date"], item["url"], item["url_object_id"], item["praise_nums"],
            item["content"], item["fav_nums"], item["front_img_url"]))
        self.conn.commit()


## adbapi 异步插入mysql
class MysqlTwistPipline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host=settings["MYSQL_HOST"],
            db=settings["MYSQL_DBNAME"],
            user=settings["MWSQL_USER"],
            passwd=settings["MYSQL_PASSWORD"],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
                insert into article(title,create_date,url,url_object_id,praise_nums,content,fav_nums,front_img_url)
                values (%s,%s,%s,%s,%s,%s,%s,%s)
                """
        cursor.execute(insert_sql, (
            item["title"], item["create_date"], item["url"], item["url_object_id"], item["praise_nums"],
            item["content"], item["fav_nums"], item["front_img_url"]))
