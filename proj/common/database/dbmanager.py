from enum import Enum, auto


from proj.common.database.mogodb import MongoDBManager
from proj.common.config.configmanager import DatabaseObject, DatabaseType

HOST = 'mongodb://192.168.137.223:27017/'


class TableType(Enum):
    Category = auto()
    Detail = auto()


class DatabaseManager:
    def __init__(self, database_list):
        # Mongo DB
        self._mongoDB: MongoDBManager = None

        self.database_list: [DatabaseObject] = database_list

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

    def insert_many_mongo(self, value) -> bool:
        return self._mongoDB.insert_many(value)

