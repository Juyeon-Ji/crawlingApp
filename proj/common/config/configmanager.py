import json
from enum import Enum, auto

from proj.common.util import Singleton


class DatabaseType(Enum):
    MONGO = auto()
    ELASTIC = auto()
    NONE = auto()


class DatabaseObject(object):
    database_type: DatabaseType
    host: str
    server: str
    port: int
    username: str
    password: str
    database_name: str
    tables: dict


class CrawlConfiguration:
    crawl_count: int = 0
    crawl_page_range = 0
    crawl_sleep_time = 0
    crawl_big_category = False
    crawl_detail_category = True
    exclude_category: list


class ConfigManager(object, metaclass=Singleton):
    database_object_list: [DatabaseObject]
    crawl_config_object: CrawlConfiguration

    def __init__(self):
        self.database_object_list: [DatabaseObject] = list()
        self.crawl_config_object: CrawlConfiguration = None

        self._load()

    def _load(self):
        path = '../resource/application.json'
        with open(path, 'r', encoding='utf-8') as f:
            json_load = json.load(f)

            self._parse(json_load)

    def _parse(self, json_load: dict):
        database_list = json_load.get('database')
        self._database_parse(database_list)

        crawl_config = json_load.get('crawl_config')
        self._crawl_config_parse(crawl_config)
        pass

    def _database_parse(self, database_list: list):
        if database_list is not None:
            database: dict
            for database in database_list:
                _dbobj = DatabaseObject()
                _dbobj.database_type = DatabaseType[database.get('database-type')]
                _dbobj.host = database.get('host')
                _dbobj.server = database.get('server')
                _dbobj.username = database.get('username')
                _dbobj.password = database.get('password')
                _dbobj.database_name = database.get('database-name')
                _dbobj.tables = database.get('tables')

                self.database_object_list.append(_dbobj)

    def _crawl_config_parse(self, crawl_config: dict):
        if crawl_config is not None:
            self.crawl_config_object = CrawlConfiguration()

            self.crawl_config_object.crawl_count = crawl_config.get('crawl-count')
            self.crawl_config_object.exclude_category = crawl_config.get('exclude-category')
            self.crawl_config_object.crawl_page_range = crawl_config.get('crawl-page-range')
            self.crawl_config_object.crawl_sleep_time = crawl_config.get('crawl-sleep-time')
            self.crawl_config_object.crawl_big_category = crawl_config.get('crawl-big-category')
            self.crawl_config_object.crawl_detail_category = crawl_config.get('crawl-detail-category')
            self.crawl_config_object.exclude_category = crawl_config.get('exclude-category')
