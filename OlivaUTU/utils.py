import OlivOS
from .config import DATA_PATH, CONF_PATH
import json
import os
import re

class Logger:
    def __init__(self):
        self._Proc = None

    def bind(self, Proc):
        self._Proc = Proc

    def _log(self, log_level: any, log_message: any, log_segment= None):
        self._Proc.log(log_level, log_message, log_segment)

    def info(self, log_message):
        self._log(2, log_message=log_message)
    
    def warn(self, log_message):
        self._log(3, log_message=log_message)

    def error(self, log_message):
        self._log(4, log_message=log_message)

def strip_leading_bot_at(msg: str, bot_id: str) -> str:
    pattern = rf'^\s*\[CQ:at,qq={bot_id}\]\s*'
    return re.sub(pattern, '', msg, count=1).strip()

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
        print('Error發生：1')
        return {}
    except json.JSONDecodeError:
        print('Error發生：2')
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