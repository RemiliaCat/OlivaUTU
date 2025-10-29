# CONST

def CREATE_DATA_UNIT(author: list[str] = [], keyword = [], reply = [], match_type = 'full'):
    return {
        'author': author,
        'keyword': keyword, # any to trigger
        'reply': reply, # random to reply
        'match_type': match_type, # full/contain
    }

def CREATE_DATA_UNION(data_units: dict = {}): 
    return {
        'data': data_units
            # 'key_hash': {
            #     DATA_UNIT
            # },
            # more to add...
    }

def CREATE_CACHE_UNIT(author: str = '', keyword = str, reply = [], match_type = 'full'):
    return {
        'author': author,
        'keyword': keyword, # any to trigger
        'reply': reply, # random to reply
        'match_type': match_type, # full/contain
    }


def CREATE_CACHE_UNION(cache_units: dict = {}):
    return {
        'data': cache_units
            # 'sbm_uuid': {
            #     CACHE_UNIT
            # },
            # more to add...
    }

DATA_PATH = 'plugin/data/OlivaUTU'
CONF_PATH = 'plugin/conf/OlivaUTU'
DEFAULT_CUSTOM_CONFIG = {
    'FILTER_GROUP_TYPE': 'blacklist', # blacklist/whitelist
    'FILTER_PRIVATE_TYPE': 'blacklist', # blacklist/whitelist
    'FILTER_GROUP_LIST': [],
    'FILTER_PRIVATE_LIST': [],
    'ADMINISTRATORS': [],
    'NEW_SUBMISSION_RECEIVE_GROUP': [],
    'NEW_SUBMISSION_RECEIVE_PRIVATE': [],
    'NEW_SUBMISSION_RECEIVED': 'You have a new applicant!\n[{sbm_uuid}] from [{author}]:\nkeyword-[{keyword}]\nreply-[{reply}]\nmatch_type-[{match_type}]',
    'SUBMISSION_DELIVERED': 'Submission [{sbm_uuid}] has already submitted!',
    'SUBMISSION_ADOPTED': 'Submission [{sbm_uuid}] has already adopted!',
    'SUBMISSION_REJECTED': 'Submission [{sbm_uuid}] has already rejected!'
}