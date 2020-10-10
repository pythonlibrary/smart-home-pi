import queue
import threading

import paho.mqtt.client as mqtt

from log import HomelabLogger
from config import config


class Session(object):

    def __init__(self, func=None) -> None:
        self._func = func

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

        self.client.connect(config['MQTT_BROKER']['HOST'], config['MQTT_BROKER']['PORT'], 60)

        self.report_thread_running = True
        self.report_thread = threading.Thread(target=self.report_status)
        self.report_thread.start()
    
    def report_status(self):
        while self.report_thread_running:
            if not ReportQ.empty():
                msg = ReportQ.get()
                # send msg with mqtt
                self.client.publish(topic=msg[0],payload=msg[1])

    def on_connect(self, client, userdata, flags, rc):

        HomelabLogger.info("Connected with result code "+str(rc))
        client.subscribe("home/+/command")

    def on_message(self, client, userdata, msg):
        message = dict({'topic': msg.topic, 'payload': msg.payload })
        if self._func is not None:
            self._func(message)
        else:
            HomelabLogger.info(msg.topic+" "+str(msg.payload))

    def loop_forever(self):
        self.client.loop_forever()
    
    def shutdown(self):
        self.report_thread_running = False

ReportQ = queue.Queue()