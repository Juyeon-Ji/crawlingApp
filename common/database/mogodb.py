""" MongoDB 관리 모듈

MongoDB Client 연결 및 DB에 접근하여 Collection 생성
수집된 데이터를 Insert 하는 모듈
"""

from enum import Enum, auto
from pymongo import MongoClient
from pymongo.database import Database


class TableType(Enum):
    """ 테이블 유형 """
    Category = auto()
    Detail = auto()


class MongoDBManager:
    """ MongoDB 관리 클래스

    Attribute

    host URL, Database 이름, Collection 이름
    """
    def __init__(self, host, database, collection):
        self.host = host
        self.database = database
        self.collection = collection

        self._client: MongoClient = None

        self.is_connect: bool = False

        self._connect()

    def _connect(self):
        self._client = MongoClient(self.host)

        if self._client is not None:
            self.is_connect = True

            self._db: Database = self._client[self.database]  # db name

    def close(self):
        """MongoDB Close"""
        if self._client is not None:
            self._client.close()

    def insert_one(self, collection: str, value: dict) -> bool:
        """ Insert One Document
        :param value: 저장할 값 (dict)
        :param collection: collection 이름

        collection 이름에 맞춰 DB에 저장

        :return  InsertOneResult """
        if self.is_connect:
            return self._db[collection].insert_one(value)
        return None

    def insert_many(self, collection: str, value):
        """ Insert many Document
        :param value: 저장할 값 (dict)
        :param collection: collection 이름

        collection 이름에 맞춰 DB에 저장

        :return InsertManyResult
        """
        if self.is_connect:
            return self._db[collection].insert_many(value)
        return None

    def find_all(self, collection: str):
        """ Find All Documnet
        :param collection: collection 이름

        collection 이름에 맞춰 DB에서 결과 조회

        :return json string
        """
        if self.is_connect:
            return self._db[collection].find()
        return None
