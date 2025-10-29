import OlivOS
from .config import CREATE_CACHE_UNION, CREATE_CACHE_UNIT, CREATE_DATA_UNION, CREATE_DATA_UNIT, DEFAULT_CUSTOM_CONFIG
from .utils import conf_path, data_path, read_json, write_json, reply_format
from .logger import logger
from . import config
from . import utils
import hashlib
import random
import uuid
import os
import re

# AI regex /submit [关键词]-[回复词](-[匹配类型])
RE_SUBMIT = re.compile(r'^\s*[./。](投稿|submit)\s+([^\s-](?:.*?[^\s-])?)-([^\s-](?:.*?[^\s-])?)(?:-([^\s-](?:.*?[^\s-])?))?\s*$', re.I)
# Non-AI regex /pass [uuid], /no [uuid]
RE_PASS = re.compile(r'^\s*[./。]pass\s*(\S+)\s*$', re.I)
RE_REJECT = re.compile(r'^\s*[./。]no\s*(\S+)\s*$', re.I)

OlivOS_Event = OlivOS.API.Event
OlivOS_Proc = OlivOS.pluginAPI.shallow
OlivOS_DB = OlivOS.userModule.UserConfDB.DataBaseAPI

# def event_filter():
#     def decorator(func):
#         def wrapper(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
#             if gconf['FILTER_GROUP_TYPE'] == 'blacklist':
#                 if plugin_event.group_id in config.FILTER_GROUP_LIST:
#                     return
#             elif gconf['FILTER_GROUP_TYPE'] == 'whitelist':
#                 if plugin_event.group_id not in config.FILTER_GROUP_LIST:
#                     return
#             if gconf['FILTER_PRIVATE_TYPE'] == 'blacklist':
#                 if plugin_event.user_id in config.FILTER_PRIVATE_LIST:
#                     return
#             elif gconf['FILTER_PRIVATE_TYPE'] == 'whitelist':
#                 if plugin_event.user_id not in config.FILTER_PRIVATE_LIST:
#                     return
#             return func(plugin_event, Proc)
#         return wrapper
#     return decorator

class Event(object):
    def init(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        global db
        db = utils.DB()
        db.bind(Proc.database)
        global global_conf
        global_conf = DEFAULT_CUSTOM_CONFIG
        global switch
        switch = True
        global logger
        logger.bind(Proc)

        if not os.path.exists(data_path()):
            os.makedirs(config.DATA_PATH)
        
        if not os.path.exists(conf_path()):
            os.makedirs(config.CONF_PATH)

        if not os.path.exists(conf_path('config')):
            write_json(config.DEFAULT_CUSTOM_CONFIG, conf_path('config'))
        global_conf = read_json(conf_path('config'))
        for k in config.DEFAULT_CUSTOM_CONFIG.keys():
            if global_conf.get(k) is None:
                global_conf[k] = config.DEFAULT_CUSTOM_CONFIG.get(k)

        if not os.path.exists(data_path('custom')):
            write_json(CREATE_DATA_UNION(), data_path('custom'))

        if not os.path.exists(data_path('cache')):
            write_json(CREATE_CACHE_UNION(), data_path('cache'))

    def init_after(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        pass

    # @event_filter
    def group_message(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        global switch
        if not switch:
            return
        unity_reply(plugin_event, Proc)
    
    # @event_filter
    def private_message(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        global switch
        if not switch:
            return
        unity_reply(plugin_event, Proc)

    def save(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        pass

    def menu(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        if plugin_event.data.event == 'plugin_on':
            logger.info('OlivaUTU high!')
            plugin_on()
        elif plugin_event.data.event == 'plugin_off':
            logger.info('OlivaUTU sad!')
            plugin_off()


def unity_reply(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
    pevent = plugin_event
    msg = pevent.data.message
    re_msg1 = RE_SUBMIT.match(msg)
    re_msg2 = RE_PASS.match(msg)
    re_msg3 = RE_REJECT.match(msg)

    # save submission, waiting for adopting
    if re_msg1 is not None:
        author = pevent.data.user_id
        keyword_raw = re_msg1.group(2)  # splitted by '|' if it's multiple word
        keyword = keyword_raw.split('|')
        keyword = [k for k in keyword if k] # ensure non-empty
        reply_raw = re_msg1.group(3)    # same as above
        reply = reply_raw.split('|')
        reply = [r for r in reply if r] # same as above
        match_type = re_msg1.group(4)
        match_type = 'full' if match_type not in ['full', 'contain'] else match_type
        sbm_uuid = str(uuid.uuid4()) # unique to identify submission

        tmp_cache_union = read_json(data_path('cache'))
        tmp_cache_unit = CREATE_CACHE_UNIT(author, keyword, reply, match_type)
        tmp_cache_union['data'][sbm_uuid] = tmp_cache_unit
        write_json(tmp_cache_union, data_path('cache'))

        msg_received = reply_format(global_conf['NEW_SUBMISSION_RECEIVED'], sbm_uuid=sbm_uuid, author=author, keyword=keyword, reply=reply, match_type=match_type)
        for group_id in global_conf.get('NEW_SUBMISSION_RECEIVE_GROUP'):
            pevent.send(message=msg_received, send_type='group', target_id=group_id)
        for user_id in global_conf.get('NEW_SUBMISSION_RECEIVE_PRIVATE'):
            pevent.send(message=msg_received, send_type='private', target_id=user_id)

        msg_submitted = reply_format(global_conf['SUBMISSION_DELIVERED'], sbm_uuid=sbm_uuid, author=author, keyword=keyword, reply=reply, match_type=match_type)
        pevent.reply(msg_submitted)

    # adopt submission after verifying, waiting for triggering
    elif re_msg2 is not None:
        if int(pevent.data.user_id) in global_conf['ADMINISTRATORS']:
            sbm_uuid = re_msg2.group(1).strip()
            tmp_cache_union = read_json(data_path('cache'))
            tmp_cache_unit = tmp_cache_union.get('data').get(sbm_uuid)
            tmp_data_union = read_json(data_path('custom'))
            if tmp_cache_unit is None:
                return
            author = tmp_cache_unit['author']
            key_hash = hashlib.md5(tmp_cache_unit['keyword'].encode()).hexdigest()
            tmp_data_union['data'][key_hash] = get_data_from_cache_unit(tmp_cache_unit)
            tmp_cache_union['data'].pop(sbm_uuid)
            write_json(tmp_data_union, data_path('custom'))
            write_json(tmp_cache_union, data_path('cache'))

            msg_adopted = reply_format(global_conf['SUBMISSION_ADOPTED'], sbm_uuid=sbm_uuid, author=author, keyword=keyword, reply=reply, match_type=match_type)
            pevent.send(send_type='private', target_id=author, message=msg_adopted)
            pevent.reply(msg_adopted)

    #reject submission after verifying
    elif re_msg3 is not None:
        if int(pevent.data.user_id) in global_conf['ADMINISTRATOR']:
            sbm_uuid = re_msg3.group(1).strip()
            tmp_cache_union:dict = read_json(data_path('cache'))
            author = tmp_cache_union.get('data').get(sbm_uuid).get(sbm_uuid)
            tmp_cache_union['data'].pop(sbm_uuid)

            msg_rejected = reply_format(global_conf['SUBMISSION_REJECTED'], sbm_uuid=sbm_uuid)
            pevent.send(send_type='private', target_id=author, message=msg_rejected)

    # choose one to reply
    else:
        key_hash = hashlib.md5(msg.encode()).hexdigest()
        tmp_data_union = read_json(data_path('custom'))
        if tmp_data_union.get('data').get(key_hash) is None:
            return
        reply = random.choice(tmp_data_union['data'][key_hash]['reply'])
        pevent.reply(reply)
    return

def plugin_on():
    global switch
    switch = True

def plugin_off():
    global switch
    switch = False

def get_data_from_cache_unit(cache_unit) -> dict:
    tmp_data_unit = CREATE_DATA_UNIT()
    tmp_data_unit['match_type'] = cache_unit.get('match_type')
    tmp_data_unit['author'].append(cache_unit.get('author'))
    tmp_data_unit['keyword'].extend(cache_unit.get('keyword'))
    tmp_data_unit['reply'].extend(cache_unit.get('reply'))
    return tmp_data_unit
