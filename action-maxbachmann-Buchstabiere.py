#!/usr/bin/env python2
# -*- coding: utf-8 -*-


import ConfigParser
import io
import paho.mqtt.client as mqtt
import random
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
    session_id = data['sessionId']
    try:
        slots = {slot['slotName']: slot['value']['value'] for slot in data['slots']}

        wort = slots['wort']
        answer = wort + ' buchstabiert sich '
        for buchstabe in wort:
            answer += buchstabe + '<break time="5000ms"/>'
        say(session_id, answer)
    except KeyError:
        pass

def say(session_id, text):
    mqtt_client.publish('hermes/dialogueManager/endSession',
                        json.dumps({'text': text, "sessionId": session_id}))




if __name__ == "__main__":
    mqtt_client.on_connect = on_connect
    mqtt_client.message_callback_add("hermes/intent/maxbachmann:buchstabiere/#", message)
    mqtt_client.connect("localhost", "1883")
    mqtt_client.loop_forever()
