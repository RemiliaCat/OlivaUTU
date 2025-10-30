# CONST
DATA_PATH = 'plugin/data/OlivaUTU'
DATA_FILE_NAME = 'custom'
CACHE_FILE_NAME = 'cache'
CONF_PATH = 'plugin/conf/OlivaUTU'
CONF_PATH_NAME = 'config'
DEFAULT_CUSTOM_CONFIG = {
    'FILTER_GROUP_TYPE': 'blacklist', # blacklist/whitelist
    'FILTER_PRIVATE_TYPE': 'blacklist', # blacklist/whitelist
    'FILTER_GROUP_LIST': [],
    'FILTER_PRIVATE_LIST': [],
    'ADMINISTRATORS': [2115963339, 88888888],
    'NEW_SUBMISSION_RECEIVE_GROUP': [],
    'NEW_SUBMISSION_RECEIVE_PRIVATE': [2115963339, 88888888],
    'NEW_SUBMISSION_RECEIVED': '你有一则新投稿申请！\n[作者]-[{author}]\n[关键词]-{keyword}\n[回复词]-{reply}\n[匹配类型]-[{match_type}]\n请使用以下命令审核：\n/pass {sbm_uuid}',
    'SUBMISSION_DELIVERED': '投稿已被提交✅，请等候审核通过\nUUID:{sbm_uuid}',
    'SUBMISSION_NOT_FOUND': 'UUID为[{sbm_uuid}]的投稿未被找到:\n404 Not Found⚠️',
    'SUBMISSION_PASSED': 'UUID为[{sbm_uuid}]的投稿已被通过！✅',
    'SUBMISSION_REJECTED': 'UUID为[{sbm_uuid}]的投稿未被通过❌',
    'DATA_DELETED': 'HASH为[{key_hash}]的回复词已删除✅',
    'DATA_NOT_FOUND': 'HASH为[{key_hash}]的回复词未被找到:\n404 Not Found⚠️'
}