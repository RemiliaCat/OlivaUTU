import OlivOS
from .config import DATA_PATH, CONF_PATH, IMAGE_PATH
import requests
import json
import os
import re

class Logger:
    '''日志记录类'''

    def __init__(self):
        self._Proc:OlivOS.pluginAPI.shallow = None

    def bind(self, Proc: OlivOS.pluginAPI.shallow) -> None:
        '''绑定Proc'''
        self._Proc = Proc

    def _log(self, log_level: any, log_message: any, log_segment= None) -> None:
        '''原始log'''
        self._Proc.log(log_level, log_message, log_segment)

    def info(self, log_message: str) -> None:
        '''log_level为info'''
        self._log(2, log_message=log_message)
    
    def warn(self, log_message: str) -> None:
        '''log_level为warn'''
        self._log(3, log_message=log_message)

    def error(self, log_message: str) -> None:
        '''log_level为error'''
        self._log(4, log_message=log_message)

def strip_leading_bot_at(msg: str, bot_id: str) -> str:
    '''清除前导CQ/OP码的at'''
    pattern = rf'^\s*\[(?:CQ:at,qq|OP:at,id)={bot_id}\]\s*'
    return re.sub(pattern, '', msg, count=1).strip()

def parse_OPcode_image(string: 'str|list') -> 'str|list':
    '''
    AI generate, 同步版本, 无法高效处理多个带图投稿请求
    解析 [OP:image,file=...,url=...] 格式,
    下载 url 对应的图片并保存为 data/images/{filename}, 
    然后将 OP 码改为 [OP:image,file=OlivaUTU/{filename}]
    '''

    # 可传入list，例如reply列表
    if isinstance(string, list):
        return [parse_OPcode_image(s) for s in string]

    pattern = re.compile(
        r'\[OP:image,file=(?P<file>[^,\]]+),url=(?P<url>[^\]]+)\]'
    )

    def repl(match):
        headers = {
        "User-Agent": (
            "Mozilla/5.0 (Linux; Android 13; M2102K1AC) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Mobile Safari/537.36 QQ/9.9.50.12345"
        ),
        "Referer": "https://qq.com/",
        }

        file_name = match.group('file')
        url = match.group('url')
        # try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(resp.status_code)
        resp.raise_for_status()
        print(imgs_path(file_name))
        with open(imgs_path(file_name), 'wb') as f:
            f.write(resp.content)
            print('hello1')
        # except Exception:
        #     print('hello2')
        #     return match.group(0)  # 保留原码以防失败
        print('hello3')
        return f'[OP:image,file=OlivaUTU/{file_name}]'
    print('hello4')
    return pattern.sub(repl, string)

def write_json(obj, path = '') -> None:
    '''覆写指定路径的json文件'''
    try:
        with open(path, 'w', encoding='utf-8') as fp:
            json.dump(obj, fp, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        return

def read_json(path = '') -> any:
    '''读取指定路径的json文件'''
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
    '''数据文件（包括缓存文件）的路径'''
    return os.path.join(DATA_PATH, f'{file_name}.json') if file_name else DATA_PATH

def conf_path(file_name=None) -> str:
    '''配置文件的路径'''
    return os.path.join(CONF_PATH, f'{file_name}.json') if file_name else CONF_PATH

def imgs_path(file_name=None) -> str:
    '''图片文件的路径'''
    return os.path.join(IMAGE_PATH, f'{file_name}') if file_name else IMAGE_PATH

def reply_format(msg: str, /, **attrs) -> str:
    '''
    匹配reply的对应参数
    若reply中未要求此参数则跳过
    若reply中要求此参数但未传递此参数，则默认为NaN
    '''
    class SafeDict(dict):
        def __missing__(self, key):
            return 'NaN'
    return msg.format_map(SafeDict(**attrs))