import json
import platform
from subprocess import Popen, PIPE
from wakeonlan import send_magic_packet

from comm import ReportQ


class ServerBase(object):

    def __init__(self, name) -> None:
        self._name = name
        self._topic_response = 'home/' + self._name + '/response'
        self._topic_broadcast_prefix = 'home/' + self._name + '/status'
    
    @property
    def name(self):
        return self._name
    
    def periodic_report(self):
        raise NotImplementedError


class LinuxServer(ServerBase):

    def __init__(self, name, mac, ip) -> None:
        super().__init__(name=name)
        self._mac = mac
        self._ip = ip

    def wake_on_lan(self, *args):
        send_magic_packet(self._mac)
        q_msg = (self._topic_response, json.dumps({"wake_up": "sent"}))
        ReportQ.put(q_msg)

    def periodic_report(self):
        pass


class DHT11Server(ServerBase):

    def __init__(self, name) -> None:
        super().__init__(name=name)
        self._humidity = 0
        self._temperature = 0
    
    @property
    def humidity(self):
        return self._humidity

    @property
    def temperature(self):
        return self._temperature
    
    def read_data(self):
        if platform.system() != 'Windows':
            process = Popen(["./dht11"], stdout=PIPE)
            (output, err) = process.communicate()
            exit_code = process.wait()

            lines = output.decode("utf-8").split('\n')

            for line in lines:
                if "=" in line:
                    data = line.split('|')
                    self._humidity = data[0].split('=')[-1].strip().split(" ")[0]
                    self._temperature = data[1].split('=')[-1].strip().split(" ")[0]
        else:
            self._humidity = 88
            self._temperature = 66
    
    def report_temperature(self, *args):
        q_msg = (self._topic_response, json.dumps({"temperature": self.temperature}))
        ReportQ.put(q_msg)

    def report_humidity(self, *args):
        q_msg = (self._topic_response, json.dumps({"humidity": self.humidity}))
        ReportQ.put(q_msg)

    def periodic_report(self):
        topic = self._topic_broadcast_prefix + '/humidity'
        q_msg = (topic, json.dumps({"value": self.humidity}))
        ReportQ.put(q_msg)
        topic = self._topic_broadcast_prefix + '/temperature'
        q_msg = (topic, json.dumps({"value": self.temperature}))
        ReportQ.put(q_msg)