class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        else:
            pass
            # 매번 __init__ 호출하고 싶으면 아래 주석 제거
            # cls._instances[cls].__init__(*args, **kwargs)
        return cls._instances[cls]


class Utils:
    @classmethod
    def join_path(cls, token, source: str, value: str) -> str:
        return token.join([source, value])

    def parse_cat_id(self, value: str) -> str:
        if value is not None:
            x = 0
            x = value.find(self.DELIMITER)
            if x != -1:
                x = x + len(self.DELIMITER) - 1
                return value[x + 1:len(value)]

    @classmethod
    def separate_right(cls, value, delimiter) -> str:
        if value is not None:
            x = 0
            x = value.find(delimiter)
            if x != -1:
                x = x + len(delimiter) - 1
                return value[x + 1:len(value)]

    @classmethod
    def separate_left(cls, value, delimiter):
        if value is not None:
            x = 0
            x = value.find(delimiter)
            if x < 1:
                return value
            else:
                return value[0: x]
