import OlivOS
from .config import DATA_PATH, CONF_PATH, IMAGE_PATH
import urllib.request
import shutil
import json
import os
import re

RE_OP_IMAGE = re.compile(r'\[OP:image,file=(?P<file>[^\],]+)(?:,url=(?P<url>[^\]]+))?\]')

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

def parse_OPcode_image(msg: 'str|list[str]') -> list[dict]:
    '''
    :brief: 解析 [OP:image,file=...,url=...] 格式,
    :param string: 要解析OPCode的字符串
    :return: 由包含file和url的字典组成的列表, 例如: [{'file':..., 'url': ...}]
    '''
    msg_str = '\n'.join(msg) if isinstance(msg, list) else msg
    print(msg_str)
    tmp_res_list = []
    for m in RE_OP_IMAGE.finditer(msg_str):
        tmp_res_list.append(m.groupdict())
    return tmp_res_list

def repl_OPcode_image(match: re.Match):
    file_name = match.group('file')
    file_path = os.path.join('OlivaUTU', file_name)
    return f'[OP:image,file={file_path}]'

def save_image(img_list: list[dict]) -> list[str]:
    '''下载QQ图片, 返回图片路径列表'''
    saved_files = []
    for img in img_list:
        file_path = imgs_path(img['file'])
        url = img['url']
        try:
            urllib.request.urlretrieve(url, file_path)
            saved_files.append(file_path)
            print('保存成功!')
        except:
            print('保存失败!')
            pass
    return saved_files
            
def delete_image(img_list: list[dict]) -> None:
    '''删除图片文件'''
    print(img_list)
    for img in img_list:
        file_path = os.path.join('data', 'images', img['file'])
        try:
            os.remove(file_path)
            print('删除成功!')
        except:
            print('删除失败!')

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