#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
import importlib
from BringApi.BringApi import BringApi
from hermes_python.hermes import Hermes
from hermes_python.ontology import *
import io
import random
import sys
import json

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def subscribe_intent_callback(hermes, intentMessage):
    action_wrapper(hermes, intentMessage, conf)


def action_wrapper(hermes, intentMessage, conf):
    if intentMessage.intent.intent_name == i18n.INTENT_ADD_ITEM:
        hermes.publish_end_session(intentMessage.session_id, addItem(hermes,intentMessage,conf))
    elif intentMessage.intent.intent_name == i18n.INTENT_DEL_ITEM:
        hermes.publish_end_session(intentMessage.session_id, deleteItem(hermes,intentMessage,conf))

def addItemList(bring, items):
    list = bring.get_items()['purchase']
    added = []
    exist = []
    for item in items:
        if not any(entr['name'] == item.value for entr in list):
            bring.purchase_item(item.value, "")
            added.append(item.value)
        else:
            exist.append(item.value)
    return added, exist
        
def addItem(hermes,intentMessage,conf):
    strout = ""
    if len(intentMessage.slots.Item) > 0:
        added, exist = addItemList(BringApi(conf['secret']['uuid'],conf['secret']['bringlistuuid']), intentMessage.slots.Item.all())
        if added:
            strout = text_list(added, i18n.ADD_START_LOT, i18n.ADD_START_ONE, i18n.ADD_END)
            strout += random.choice(i18n.ADD_F_START) if exist else random.choice(i18n.ADD_CLOSE)
        if exist:
            strout += text_list(exist, i18n.ADD_F_START_LOT, i18n.ADD_F_START_ONE, i18n.ADD_F_END)
    else:
        strout = random.choice(i18n.ADD_WHAT)
    return strout

# create response of pattern:
# XXX, XXX and XXX have been added. {lot} {end}
# XXX has been added. {one} {end}
def text_list(itemlist, lot, one, end):
    if len(itemlist) > 1:
        response = random.choice(lot).format(first=", ".join(itemlist[:-1]), last=itemlist[-1])
    else:
        response = random.choice(one).format(itemlist[0])
    response = str_temp + random.choice(end)
    return response


def deleteItem(hermes,intentMessage,conf):
    return "wurde von der Einkaufsliste gelöscht!"

if __name__ == "__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    conf = read_configuration_file(CONFIG_INI)
    with open("/usr/share/snips/assistant/assistant.json") as json_file:
            language = json.load(json_file)["language"]
    i18n = importlib.import_module("translations." + language)

    with Hermes("localhost:1883") as h:
        h.subscribe_intents(subscribe_intent_callback).start()
