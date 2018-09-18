#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import ConfigParser
import io
import paho.mqtt.client as mqtt
import time
import json

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section: {option_name: option for option_name, option in self.items(section)} for section in self.sections()}


def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()


conf = read_configuration_file(CONFIG_INI)
print("Conf:", conf)

# MQTT client to connect to the bus
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    client.subscribe("hermes/intent/#")


def message(client, userdata, msg):
    data = json.loads(msg.payload.decode("utf-8"))
    siteId = data['siteId']
    session_id = data['sessionId']
    try:
        slots = {slot['slotName']: slot['value']['value'] for slot in data['slots']}

        wort = slots['wort']
        answer = wort + ' buchstabiert sich '
        mqtt_client.publish('hermes/dialogueManager/endSession',
                        json.dumps({"sessionId": session_id}))
        ttssay(siteId, answer)
        for buchstabe in wort:
            ttssay(siteId, buchstabe)
            time.sleep(1)
    except KeyError:
        pass

def ttssay(siteId, text):
    mqtt_client.publish('hermes/tts/say',
                        json.dumps({'text': text, "siteId": siteId, "lang": "de"}))




if __name__ == "__main__":
    mqtt_client.on_connect = on_connect
    mqtt_client.message_callback_add("hermes/intent/maxbachmann:buchstabiere/#", message)
    mqtt_client.connect("localhost", "1883")
    mqtt_client.loop_forever()
