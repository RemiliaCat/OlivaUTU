import OlivOS
from dataclasses import dataclass, field

OlivOS_DB = OlivOS.userModule.UserConfDB.DataBaseAPI

def gen_list():
    return []

@dataclass
class DataUnit:
    author: list[str] = field(default_factory=gen_list)
    keyword: str = ''
    reply: list[str] = field(default_factory=gen_list)
    match_type: str = ''

@dataclass
class CacheUnit:
    author: str = ''
    keyword: str = ''
    reply: list[str] = field(default_factory=gen_list)
    match_type: str = ''

@dataclass
class DataUnion:
    data: DataUnit

@dataclass
class CacheUnion:
    data: CacheUnit

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

def create_data_unit(author: 'list[str]|None' = None, keyword: str = '', reply: 'str|list[str]' = None, match_type: str = 'full'):
    if author is None:
        author = []
    if reply is None:
        reply = []
    elif isinstance(reply, str):
        reply = [reply]
    return {
        'author': author,
        'keyword': keyword, # any to trigger
        'reply': reply, # random to reply
        'match_type': match_type, # full/contain
    }

def create_data_union(data_units: dict = None): 
    if data_units is None:
        data_units = {}
    return {
        'data': data_units
            # 'key_hash': {
            #     DATA_UNIT
            # },
            # more to add...
    }

def create_cache_unit(author: str = '', keyword: str = '', reply: 'str|list[str]' = None, match_type: str = 'full'):
    if reply is None:
        reply = []
    elif isinstance(reply, str):
        reply = [reply]
    return {
        'author': author,
        'keyword': keyword, # any to trigger
        'reply': reply, # random to reply
        'match_type': match_type, # full/contain
    }


def create_cache_union(cache_units: dict = None):
    if cache_units is None:
        cache_units = {}
    return {
        'data': cache_units
            # 'sbm_uuid': {
            #     CACHE_UNIT
            # },
            # more to add...
    }

def get_data_from_cache_unit(cache_unit, data_unit = None) -> dict[str, any]:

    reply = cache_unit.get('reply')
    if isinstance(reply, str):
        reply = [reply]
    elif reply is None:
        reply = []

    tmp_data_unit = data_unit
    if data_unit is None:
        tmp_data_unit = create_data_unit()
    tmp_data_unit['match_type'] = cache_unit.get('match_type')
    if cache_unit.get('author') not in tmp_data_unit['author']:
        tmp_data_unit['author'].append(cache_unit.get('author'))
    tmp_data_unit['keyword'] = cache_unit.get('keyword')
    tmp_data_unit['reply'].extend(cache_unit.get('reply'))
    return tmp_data_unit