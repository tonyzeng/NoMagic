#!/usr/bin/env python
# -*- coding: utf8 -*-

import uuid
import json

#import pickle
#import binascii
#import zlib
#import hashlib
#import random
#import string


from setting import settings

from setting import conn
from setting import ring as connections

_NUMBER = len(connections)


def _pack(data): return json.dumps(data, ensure_ascii=False)
def _unpack(data): return json.loads(data)
def _key(data): return data

def _new_key(): return uuid.uuid4().hex
def _number(key): return int(key, 16) % _NUMBER


def _get_entity_by_id(entity_id):
    entity = connections[_number(entity_id)].get("SELECT body FROM entities WHERE id = %s", _key(entity_id))
    return _unpack(entity["body"]) if entity else None

def _get_entities_by_ids(entity_ids):
    entities = []

    for h in range(_NUMBER):
        ids = [i for i in entity_ids if h == _number(i)]

        if len(ids) > 1:
            entities.extend([(i["id"], _unpack(i["body"])) for i in connections[h].query("SELECT * FROM entities WHERE id IN %s" % str(tuple(ids)))])
        elif len(ids) == 1:
            entity = _get_entity_by_id(ids[0])
            entities.extend([(ids[0], entity)] if entity else [])

    entities = dict(entities)
    return [(i, entities[i]) for i in entity_ids]

def _update_entity_by_id(entity_id, data):
    assert connections[_number(entity_id)].execute_rowcount("UPDATE entities SET body = %s WHERE id = %s", _pack(data), _key(entity_id))
