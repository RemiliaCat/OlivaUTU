import OlivOS
from dataclasses import dataclass, field

OlivOS_DB = OlivOS.userModule.UserConfDB.DataBaseAPI

def _gen_list():
    return []

@dataclass
class DataUnit:
    key_hash: str = ''
    author: list[str] = field(default_factory=_gen_list)
    keyword: str = ''
    reply: list[str] = field(default_factory=_gen_list)
    match_type: str = ''

@dataclass
class CacheUnit:
    sbm_uuid: str = ''
    author: str = ''
    keyword: str = ''
    reply: list[str] = field(default_factory=_gen_list)
    match_type: str = ''

class DB:
    '''
    数据库类
    使用了@rainboat的userConfDB模块，主要使用该模块提供的更低级接口
    '''

    def __init__(self):
        self.db: OlivOS_DB = None
        self.namespace: str = None

    def bind(self, database: OlivOS_DB, namespace: str = 'OlivaUTU') -> None:
        '''绑定userConfDB的database'''
        self.db = database
        self.namespace = namespace

    def set_data_from_DataUnit(self, unit: DataUnit):
        '''通过传入DataUnit来存储数据，通过key_hash区分每一个DataUnit，自动填写了namespace'''
        key_hash = unit.key_hash
        author = unit.author
        keyword = unit.keyword
        reply = unit.reply
        match_type = unit.match_type
        self.db.set_config(namespace=self.namespace, key='key_hash', value=key_hash, basic_hashed=key_hash, pkl=False)
        self.db.set_config(namespace=self.namespace, key='author', value=author, basic_hashed=key_hash, pkl=True)
        self.db.set_config(namespace=self.namespace, key='keyword', value=keyword, basic_hashed=key_hash, pkl=False)
        self.db.set_config(namespace=self.namespace, key='reply', value=reply, basic_hashed=key_hash, pkl=True)
        self.db.set_config(namespace=self.namespace, key='match_type', value=match_type, basic_hashed=key_hash, pkl=False)

    def set_data_from_CacheUnit(self, unit: CacheUnit):
        '''通过传入CacheUnit来传入数据，通过sbm_uuid区分每一个CacheUnit，自动填写了namespace'''
        sbm_uuid = unit.sbm_uuid
        author = unit.author
        keyword = unit.keyword
        reply = unit.reply
        match_type = unit.match_type
        self.db.set_config(namespace=self.namespace, key='key_hash', value=sbm_uuid, basic_hashed=sbm_uuid, pkl=False)
        self.db.set_config(namespace=self.namespace, key='author', value=author, basic_hashed=sbm_uuid, pkl=True)
        self.db.set_config(namespace=self.namespace, key='keyword', value=keyword, basic_hashed=sbm_uuid, pkl=False)
        self.db.set_config(namespace=self.namespace, key='reply', value=reply, basic_hashed=sbm_uuid, pkl=True)
        self.db.set_config(namespace=self.namespace, key='match_type', value=match_type, basic_hashed=sbm_uuid, pkl=False)

    def get_data_as_DataUnit(self, key_hash):
        pass

    def get_data_as_CacheUnit(self, sbm_uuid):
        pass

    def get_data(self, key: str, hash: 'str|None' = None, default_value: any = None, pkl: bool = True) -> any:
        '''对低级接口get_config()的封装，自动填写了namespace'''
        return self.db.get_config(namespace=self.namespace, key=key, basic_hashed=hash, default_value=default_value, pkl=pkl)
    
    def set_data(self, key: str, value: 'any', hash: 'str|None' = None, pkl: bool = True) -> bool:
        '''对低级接口set_config()的封装，自动填写了namespace'''
        return self.db.set_config(self.namespace, key=key,  value=value, basic_hashed=hash, pkl=pkl)

def create_data_unit(author: 'list[str]|None' = None, keyword: str = '', reply: 'str|list[str]' = None, match_type: str = 'full') -> dict:
    '''data_unit数据结构的工厂创建方法'''
    if author is None:
        author = []
    if reply is None:
        reply = []
    elif isinstance(reply, str):
        reply = [reply]
    return {
        'author': author,
        'keyword': keyword,
        'reply': reply,
        'match_type': match_type
    }

def create_data_union(data_units: 'dict|None' = None) -> dict: 
    '''data_union数据结构的工厂创建方法'''
    if data_units is None:
        data_units = {}
    return {
        'data': data_units
            # 'key_hash': {
            #     DATA_UNIT
            # },
            # more to add...
    }

def create_cache_unit(author: str = '', keyword: str = '', reply: 'str|list[str]' = None, match_type: str = 'full') -> dict:
    '''cache_unit数据结构的工厂创建方法'''
    if reply is None:
        reply = []
    elif isinstance(reply, str):
        reply = [reply]
    return {
        'author': author,
        'keyword': keyword,
        'reply': reply,
        'match_type': match_type
    }


def create_cache_union(cache_units: dict = None) -> dict:
    '''cache_union数据结构的工厂创建方法'''
    if cache_units is None:
        cache_units = {}
    return {
        'data': cache_units
            # 'sbm_uuid': {
            #     CACHE_UNIT
            # },
            # more to add...
    }

def get_data_from_cache(cache_unit, data_unit = None) -> dict:
    '''将cache_unit转换为data_unit'''
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