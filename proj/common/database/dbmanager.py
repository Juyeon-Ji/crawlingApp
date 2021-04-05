from enum import Enum, auto


from proj.common.database.mogodb import MongoDBManager
from proj.common.config.configmanager import ConfigManager, DatabaseObject, DatabaseType
from proj.common.util import Singleton

HOST = 'mongodb://192.168.137.223:27017/'


class TableType(Enum):
    Category = auto()
    Detail = auto()


class DatabaseManager(object, metaclass=Singleton):
    def __init__(self):
        # Mongo DB
        self._mongoDB: MongoDBManager = None

        self.database_list: [DatabaseObject] = ConfigManager().database_object_list

        self._load()

    def _load(self):
        for item in self.database_list:
            database: DatabaseObject = item
            if DatabaseType.MONGO == database.database_type:
                self._mongoDB = MongoDBManager(host=database.host,
                                               database=database.database_name,
                                               collection=database.tables)

            elif DatabaseType.ELASTIC == database.database_type:
                pass

    def close(self):
        if self._mongoDB is not None:
            self._mongoDB.close()

    def insert_one_mongo(self, collection: str, value) -> bool:
        return self._mongoDB.insert_one(collection, value)

    def insert_many_mongo(self, collection: str, value) -> bool:
        return self._mongoDB.insert_many(collection, value)

    def find_all_mongo(self, collection: str):
        return self._mongoDB.find_all(collection)

