import json
import time

import click
from apscheduler.schedulers.background import BackgroundScheduler


from comm import Session
from server import LinuxServer, DHT11Server
from log import HomelabLogger


#########################################################################################
# Main function begins here
#########################################################################################
@click.command()
def main():

    nextcloud_server = LinuxServer('nextcloud-server', 'AB:CE:FE:1C:BD:3D', '10.0.0.108')
    pi0_dht11_server = DHT11Server('pi-zero-dht11')

    servers = []
    servers.append(nextcloud_server)
    servers.append(pi0_dht11_server)

    def message_handler(msg):
        HomelabLogger.info(msg)
        try:
            topic_parts = msg['topic'].split('/')
            target_server = topic_parts[1] 
            msg_type = topic_parts[2] 

            payload = msg['payload']

            for server in servers:
                if server.name == target_server and msg_type == 'command':
                    # decode message body
                    command = json.loads(payload)

                    if hasattr(server, command['name']):
                        fun = getattr(server, command['name'])
                        if 'time' not in command.keys():
                            # run immediately
                            fun(*command['parameter'])
                        else:
                            # use scheduler to schedule a task
                            pass
                    # execute and break
                    break
        except Exception as e:
            HomelabLogger.error('!!!!!! error happend for message:')
            HomelabLogger.error(e)


    scheduler = BackgroundScheduler()

    scheduler.add_job(pi0_dht11_server.read_data, 'interval', [], minutes=1)
    scheduler.add_job(pi0_dht11_server.periodic_report, 'interval', [], minutes=1)

    scheduler.start()


    session = Session(func=message_handler)

    try:
        session.loop_forever()
    except KeyboardInterrupt:
        session.shutdown()
    

#########################################################################################
if __name__ == '__main__':
    main()
