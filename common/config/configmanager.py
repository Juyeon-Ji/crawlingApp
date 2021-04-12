""" 설정 정보를 로드 관리하는 모듈



"""

import json
from enum import Enum, auto

from common.util import Singleton


class DatabaseType(Enum):
    """
    Database 유형에 따른 Enum Class
    """
    MONGO = auto()
    ELASTIC = auto()
    NONE = auto()


class DatabaseObject:  # pylint: disable=too-few-public-methods
    """
    Database 설정 정보에 대한 Dataclass
    """
    database_type: DatabaseType
    host: str
    server: str
    port: int
    username: str
    password: str
    database_name: str
    tables: dict


class CrawlConfiguration:  # pylint: disable=too-few-public-methods
    """
    Crawl Config 정보에 대한 Dataclass
    """
    category_id: int = 50000000
    crawl_count: int = 0
    crawl_page_range = 0
    crawl_sleep_time = 0
    crawl_big_category = False
    crawl_detail_category = True
    exclude_category: list
    crawl_category: list


class ConfigManager(metaclass=Singleton):
    """ Config 정보를 관리하고 로드하는 클래스

    설정 정보 파일(application.json)을 로드하고 관리하는 class 입니다.
    """
    database_object_list: [DatabaseObject]
    crawl_config: CrawlConfiguration

    def __init__(self):
        """ DatabaseObject list 와 CrawlConfiguration 으로 초기화 합니다.
        바로 _load()를 합니다. """
        self.database_object_list: [DatabaseObject] = list()
        self.crawl_config: CrawlConfiguration = None

        self._load()

    def get_database_object(self) -> [DatabaseObject]:
        """" Database Object 목록을 전달합니다.

        :return [DatabaseObject]"""
        if self.database_object_list.count() > 0:
            return self.database_object_list

        return None

    def get_crawl_config(self) -> CrawlConfiguration:
        """ Crawl Config 정보를 전달합니다.

        :return CrawlConfiguration"""
        if self.crawl_config is not None:
            return self.crawl_config

        return None

    def _load(self):
        """ 설정 정보 파일 Load

        json 모듈을 이용하여 파일을 로드합니다."""
        path = 'resource/application.json'
        with open(path, 'r', encoding='utf-8') as __file:
            json_load = json.load(__file)

            self._parse(json_load)

    def _parse(self, json_load: dict):
        """json 정보를 파싱합니다.

        :argument json_load:dict
            database 관련 key: database
            crawl configuration 관련 key : crawl_config

        get 한 데이터를 각 파싱 함수로 전달합니다.
        """
        database_list = json_load.get('database')
        self._database_parse(database_list)

        crawl_config = json_load.get('crawl_config')
        self._crawl_config_parse(crawl_config)

    def _database_parse(self, database_list: list):
        """ Database Config 정보를 파싱하여 리스트에 저장 """
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
        """ Crawl Config 정보를 파싱하여 객체에 주입 """
        if crawl_config is not None:
            self.crawl_config = CrawlConfiguration()

            self.crawl_config.crawl_count = crawl_config.get('crawl-count')
            self.crawl_config.exclude_category = crawl_config.get('exclude-category')
            self.crawl_config.crawl_page_range = crawl_config.get('crawl-page-range')
            self.crawl_config.crawl_sleep_time = crawl_config.get('crawl-sleep-time')
            self.crawl_config.crawl_big_category = crawl_config.get('crawl-big-category')
            self.crawl_config.crawl_detail_category = crawl_config.get('crawl-detail-category')
            self.crawl_config.exclude_category = crawl_config.get('exclude-category')
            self.crawl_config.crawl_category = crawl_config.get('crawl-category-list')
            self.crawl_config.category_id = int(crawl_config.get('category-id'))
