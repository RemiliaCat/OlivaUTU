import OlivOS
from .utils import conf_path, data_path, read_json, write_json, reply_format
from .config import DEFAULT_CUSTOM_CONFIG, DATA_FILE_NAME, CACHE_FILE_NAME
from . import config
from . import utils
from . import data
import hashlib
import random
import uuid
import os
import re

# /submit [关键词]-[回复词](-[匹配类型])
RE_SUBMIT = re.compile(r'^\s*[./。](?:投稿|submit|sbm)\s*(.+)$', re.I | re.S)
# /pass [uuid], /reject [uuid]
RE_REVIEW = re.compile(r'^\s*[./。](pass|adopt|采纳|通过|no|reject|拒绝)\s*(.+)$', re.I)
# /getHash [关键词]
RE_GETHASH = re.compile(r'^\s*[./。]gethash\s*(.+)$', re.I | re.S)

# 类型别名设置
OlivOS_Event = OlivOS.API.Event
OlivOS_Proc = OlivOS.pluginAPI.shallow
OlivOS_DB = OlivOS.userModule.UserConfDB.DataBaseAPI

# 事件入口
class Event(object):
    def init(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        global db
        db = data.DB()
        db.bind(Proc.database)
        global gconf
        gconf = DEFAULT_CUSTOM_CONFIG
        global glogger
        glogger = utils.Logger()
        glogger.bind(Proc)
        unity_load()

    def init_after(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        pass

    def group_message(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        if gconf['FILTER_GROUP_TYPE'].lower() == 'blacklist':
            if plugin_event.data.group_id in gconf['FILTER_GROUP_LIST']:
                return
        elif gconf['FILTER_GROUP_TYPE'].lower() == 'whitelist':
            if plugin_event.data.group_id not in gconf['FILTER_GROUP_LIST']:
                return
        if db.get_data('switch', True, False):
            unity_reply(plugin_event, Proc)
    
    def private_message(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        if gconf['FILTER_PRIVATE_TYPE'].lower() == 'blacklist':
            if plugin_event.data.user_id in gconf['FILTER_PRIVATE_LIST']:
                return
        elif gconf['FILTER_PRIVATE_TYPE'].lower() == 'whitelist':
            if plugin_event.data.user_id not in gconf['FILTER_PRIVATE_LIST']:
                return
        if db.get_data('switch', True, False):
            unity_reply(plugin_event, Proc)

    def save(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        pass

    def menu(plugin_event:OlivOS_Event, Proc:OlivOS_Proc):
        if plugin_event.data.event == 'plugin_on':
            glogger.info('o(≧▽≦)o: OlivaUTU is running!')
            plugin_on()
        elif plugin_event.data.event == 'plugin_off':
            glogger.info('/(>.<)/~~: OlivaUTU get sad!')
            plugin_off()
        elif plugin_event.data.event == 'plugin_reload':
            unity_load()
            glogger.info('owo: OlivaUTU turned around!')

# 具体逻辑处理区
def unity_reply(plugin_event:OlivOS_Event, Proc:OlivOS_Proc) -> None:
    '''统一回复消息事件'''
    pevent = plugin_event
    msg_raw = pevent.data.message
    msg = utils.strip_leading_bot_at(msg_raw, pevent.bot_info.id)

    sbm_cmd = parse_sbm_cmd(msg)
    if sbm_cmd is not None:
        # 通过 /sbm add [关键词]-[回复词]-[匹配模式] 提交投稿，其中`add`和匹配模式可省略
        if sbm_cmd['action'] == 'add':
            sbm_uuid = str(uuid.uuid4())
            author = pevent.data.user_id
            keyword = sbm_cmd['keyword']
            reply = sbm_cmd['reply']
            match_type = sbm_cmd['match_type']
            handle_sbm_add(
                pevent=pevent,
                sbm_uuid=sbm_uuid,
                author=author,
                keyword=keyword,
                reply=reply,
                match_type=match_type
            )
        # 删除指定key_hash的data_unit，若只需删除特定回复请转到plugin/data/OlivaUTU/{DATA_FILE_NAME}
        elif sbm_cmd['action'] == 'del':
            key_hash = sbm_cmd['key_hash']
            handle_sbm_del(pevent=pevent, key_hash=key_hash)
        # 显示指定key_hash的回复词信息
        elif sbm_cmd['action'] == 'show':
            if pevent.data.user_id in gconf['ADMINISTRATORS']:
                key_hash = sbm_cmd['key_hash']
                handle_sbm_show(pevent=pevent, key_hash=key_hash)
        # 暂定显示所有key_hash及其对应keyword，可能改为近30个回复词
        elif sbm_cmd['action'] == 'list':
            if  pevent.data.user_id in gconf['ADMINISTRATORS']:
                handle_sbm_list
        return
    
    rev_cmd = parse_rev_cmd(msg)
    if rev_cmd is not None:
        if pevent.data.user_id in str(gconf['ADMINISTRATORS']):
            # /pass [uuid]
            if rev_cmd['action'] == 'pass':
                sbm_uuid = rev_cmd['uuid']
                handle_rev_pass(pevent=pevent, sbm_uuid=sbm_uuid)
            
            # /reject [uuid]，由于`/r`会触发OlivaDice的指令，这里提供了别名/no, /拒绝
            elif rev_cmd['action'] == 'reject':
                sbm_uuid = rev_cmd['uuid']
                handle_rev_reject(pevent=pevent, sbm_uuid=sbm_uuid)
        return
    
    # /getHash [关键词] 获取`关键词文本hash`
    ghs_match = RE_GETHASH.match(msg)
    if ghs_match is not None:
        keyword = ghs_match.group(1).strip()
        key_hash = hashlib.md5(keyword.encode()).hexdigest()
        pevent.reply(key_hash)
        return
    
    # 通过`消息文本hash`匹配`关键词文本hash`
    key_hash = hashlib.md5(msg.encode()).hexdigest()
    tmp_data_union = read_json(data_path(DATA_FILE_NAME))
    if tmp_data_union.get('data').get(key_hash) is None:
        return
    if tmp_data_union.get('data').get(key_hash).get('reply').empty():
        return
    msg_reply = random.choice(tmp_data_union['data'][key_hash]['reply'])
    pevent.reply(msg_reply)
    pevent.set_block(True)
    return

def unity_load() -> None:
    '''统一加载配置文件'''
    global gconf
    if not os.path.exists(data_path()):
        os.makedirs(config.DATA_PATH)
    
    if not os.path.exists(conf_path()):
        os.makedirs(config.CONF_PATH)

    if not os.path.exists(conf_path('config')):
        write_json(config.DEFAULT_CUSTOM_CONFIG, conf_path('config'))
    gconf = read_json(conf_path('config'))
    for k in config.DEFAULT_CUSTOM_CONFIG.keys():
        if gconf.get(k) is None:
            gconf[k] = config.DEFAULT_CUSTOM_CONFIG.get(k)
    write_json(gconf, conf_path('config'))

    if not os.path.exists(data_path(DATA_FILE_NAME)):
        write_json(data.create_data_union(), data_path(DATA_FILE_NAME))

    if not os.path.exists(data_path(CACHE_FILE_NAME)):
        write_json(data.create_cache_union(), data_path(CACHE_FILE_NAME))

def plugin_on() -> None:
    '''menu事件中的plugin_on事件处理'''
    db.set_data('switch', True, False)

def plugin_off() -> None:
    '''menu事件中的plugin_off事件处理'''
    db.set_data('switch', False, False)

def plugin_reload() -> None:
    '''menu事件中的plugin_reload事件处理'''
    unity_load()

def handle_sbm_add(pevent, sbm_uuid, author, keyword, reply, match_type) -> None:
    '''处理sbm命令中的add子命令'''
    tmp_cache_union = read_json(data_path(CACHE_FILE_NAME))
    tmp_cache_unit = data.create_cache_unit(author, keyword, reply, match_type)
    tmp_cache_union['data'][sbm_uuid] = tmp_cache_unit
    write_json(tmp_cache_union, data_path(CACHE_FILE_NAME))

    if pevent.data.user_id in gconf['WHITE_USERS']:
        handle_rev_pass()
        return

    msg_received = reply_format(gconf['NEW_SUBMISSION_RECEIVED'], sbm_uuid=sbm_uuid, author=author, keyword=keyword, reply=reply, match_type=match_type)
    for group_id in gconf.get('NEW_SUBMISSION_RECEIVE_GROUP'):
        pevent.send(message=msg_received, send_type='group', target_id=group_id)
    for user_id in gconf.get('NEW_SUBMISSION_RECEIVE_PRIVATE'):
        pevent.send(message=msg_received, send_type='private', target_id=user_id)

    msg_submitted = reply_format(gconf['SUBMISSION_DELIVERED'], sbm_uuid=sbm_uuid, author=author, keyword=keyword, reply=reply, match_type=match_type)
    pevent.reply(msg_submitted)

def handle_sbm_del(pevent, key_hash) -> None:
    '''处理sbm命令中的del子命令'''
    tmp_data_union = read_json(data_path(DATA_FILE_NAME))
    tmp_data_unit = tmp_data_union.get('data').get(key_hash)
    if tmp_data_union['data'].get(key_hash) is not None:
        tmp_data_unit = tmp_data_union['data'][key_hash]
        author = tmp_data_unit.get('author')
        keyword = tmp_data_unit.get('keyword')
        reply = tmp_data_unit.get('reply')
        match_type = tmp_data_unit.get('match_type')
        tmp_data_union['data'].pop(key_hash)
        write_json(tmp_data_union, data_path(DATA_FILE_NAME))
        msg_deleted = reply_format(gconf['DATA_DELETED'],key_hash=key_hash, author=author, keyword=keyword, reply=reply, match_type=match_type)
    msg_deleted = reply_format(gconf['DATA_NOT_FOUND'],key_hash=key_hash)
    pevent.reply(msg_deleted)

def handle_sbm_show(pevent, key_hash) -> None:
    '''处理sbm命令中的show子命令'''
    tmp_data_union = read_json(data_path(DATA_FILE_NAME))
    tmp_data_unit = tmp_data_union.get('data').get(key_hash)
    if tmp_data_union is None:
        msg_not_found = reply_format(gconf['DATA_NOT_FOUND'], key_hash=key_hash)
        pevent.reply(msg_not_found)
    author = tmp_data_unit.get('author')
    keyword = tmp_data_unit.get('keyword')
    reply = tmp_data_unit.get('reply')
    match_type = tmp_data_unit.get('match_type')
    msg_show_data = reply_format(gconf['DATA_SHOW'], key_hash=key_hash, author=author, keyword=keyword, reply=reply, match_type=match_type)
    pevent.reply(msg_show_data)

def handle_sbm_list(pevent) -> None:
    '''处理sbm命令中的list子命令'''
    tmp_data_union = read_json(data_path(DATA_FILE_NAME))
    tmp_res_raw = {}
    for key_hash, unit in tmp_data_union.get('data').items():
        tmp_res_raw[key_hash] = unit['keyword']
    tmp_res = '\n'.join(f'{v}:\n{k}' for k, v in tmp_res_raw.items())
    pevent.reply(tmp_res)

def handle_rev_pass(pevent, sbm_uuid) -> None:
    '''处理审核系统中的pass命令'''
    tmp_cache_union = read_json(data_path(CACHE_FILE_NAME))
    tmp_cache_unit = tmp_cache_union.get('data').get(sbm_uuid)
    if tmp_cache_unit is None:
        msg_not_found = reply_format(gconf['SUBMISSION_NOT_FOUND'], sbm_uuid=sbm_uuid)
        pevent.reply(msg_not_found)
        return
    
    author = tmp_cache_unit.get('author')
    keyword = tmp_cache_unit.get('keyword')
    reply = tmp_cache_unit.get('reply')
    match_type = tmp_cache_unit.get('match_type')
    key_hash = hashlib.md5(keyword.encode()).hexdigest()
    tmp_data_union = read_json(data_path(DATA_FILE_NAME))
    tmp_data_unit = tmp_data_union.get('data').get(key_hash)
    tmp_data_union['data'][key_hash] = data.get_data_from_cache(tmp_cache_unit, tmp_data_unit)
    tmp_cache_union['data'].pop(sbm_uuid)
    write_json(tmp_data_union, data_path(DATA_FILE_NAME))
    write_json(tmp_cache_union, data_path(CACHE_FILE_NAME))

    msg_passed = reply_format(gconf['SUBMISSION_PASSED'], sbm_uuid=sbm_uuid, author=author, keyword=keyword, reply=reply, match_type=match_type)
    pevent.send(send_type='private', target_id=author, message=msg_passed)
    pevent.reply(msg_passed)

def handle_rev_reject(pevent, sbm_uuid) -> None:
    '''处理审核系统中的reject命令'''
    tmp_cache_union = read_json(data_path(CACHE_FILE_NAME))
    tmp_cache_unit = tmp_cache_union.get('data').get(sbm_uuid)
    if tmp_cache_unit is not None:
        author = tmp_cache_unit.get('author')
        keyword = tmp_cache_unit.get('keyword')
        reply = tmp_cache_unit.get('reply')
        match_type = tmp_cache_unit.get('match_type')
    tmp_cache_union['data'].pop(sbm_uuid)
    write_json(tmp_cache_union, data_path(CACHE_FILE_NAME))

    msg_rejected = reply_format(gconf['SUBMISSION_REJECTED'], sbm_uuid=sbm_uuid, author=author, keyword=keyword, reply=reply, match_type=match_type)
    pevent.send(send_type='private', target_id=author, message=msg_rejected)
    pevent.reply(msg_rejected)

def parse_sbm_cmd(msg: str) -> 'dict|None':
    '''
    解析: /submit add/del/show 命令
    参数: msg 不多介绍
    返回 dict | None:
      {
        "action": "add" | "del" | "show" | "list",
        "keyword": ...,
        "reply": list[str],
        "match_type": "full" | "contain",
        "key_hash": ...
      }
    如果不匹配会返回None
    '''
    m = RE_SUBMIT.match(msg.strip())
    if not m:
        return None
    body = m.group(1).strip()

    if body.lower().startswith('del'):
        key_hash = body[3:].strip()
        if not key_hash:
            return None
        return {'action': 'del', 'key_hash': key_hash}
    
    if body.lower().startswith('show'):
        key_hash = body[4:].strip()
        if not key_hash:
            return None
        return {'action': 'show', 'key_hash': key_hash}
    
    if body.lower() == 'list':
        return {'action': 'list'}
    
    # if body.lower().startswith('add'):
    parts = []
    buf = ''

    # 检测CQ/OP码
    inside = False
    for i, ch in enumerate(body):
        if ch == '[':
            if body[i:i+4] == '[CQ:' or body[i:i+4] == '[OP:':
                inside = True
        elif ch == ']' and inside:
            inside = False
        if ch == '-' and not inside and len(parts) < 2:
            parts.append(buf.strip())
            buf = ''
        else:
            buf += ch
    parts.append(buf.strip())

    if len(parts) < 2:
        return None
    keyword = parts[0].strip()
    reply_raw = parts[1].strip()
    reply = [r.strip() for r in reply_raw.split('|') if r.strip()]
    match_type = (parts[2].lower() if len(parts) >= 3 else 'full')
    if match_type not in ['full', 'contain']:
        match_type = 'full'

    if not keyword or not reply:
        return None

    return {
        'action': 'add',
        'keyword': keyword,
        'reply': reply,
        'match_type': match_type
    }

def parse_rev_cmd(msg: str) -> 'dict|None':
    """
    解析 /pass [uuid] 和 /reject [uuid] 命令
    返回: dict | None
      {
        "action": "pass" | "reject",
        "uuid": "<uuid>",
      }
    如果不匹配返回 None
    """
    m = RE_REVIEW.match(msg)
    if not m:
        return None
    
    head_cmd = m.group(1).strip()
    if head_cmd.lower() in ['no', 'reject', '拒绝']:
        action = 'reject'
    elif head_cmd.lower() in ['pass', 'adopt', '采纳', '通过']:
        action = 'pass'

    uuid = m.group(2).strip()

    if not uuid:
        return None
    
    return {
        'action': action,
        'uuid': uuid
    }