import OlivOS
from .config import DATA_PATH, CONF_PATH
from .logger import logger
import json
import os

OlivOS_DB = OlivOS.userModule.UserConfDB.DataBaseAPI

class DB:
    def __init__(self):
        self.db: OlivOS_DB = None
        self.namespace: str = None

    def bind(self, database, namespace: str = 'OlivaUTU'):
        self.db = database
        self.namespace = namespace

    def get_data(self, key: str, default_value: any = None, pkl: bool = True):
        return self.db.get_basic_config(namespace=self.namespace, key=key, default_value=default_value, pkl=pkl)
    
    def set_data(self, key: str, value: any, pkl: bool = True):
        return self.db.set_basic_config(namespace=self.namespace, key=key, value=value, pkl=pkl)

def write_json(obj, path = '') -> None:
    try:
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(obj, fp, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        return

def read_json(path = '') -> any:
    try:
        with open(path, 'r', encoding='utf-8') as fp:
            return json.load(fp)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        logger.info(f"JSON decode failed at {path}, returning empty dict")
        return {}

def data_path(file_name=None) -> str:
    return os.path.join(DATA_PATH, f'{file_name}.json') if file_name else DATA_PATH

def conf_path(file_name=None) -> str:
    return os.path.join(CONF_PATH, f'{file_name}.json') if file_name else CONF_PATH

# mapping attr like '{keyword}' if given
def reply_format(msg: str, /, **attrs):
    class SafeDict(dict):
        def __missing__(self, key):
            return '{' + key + '}'
    return msg.format_map(SafeDict(**attrs))