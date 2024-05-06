from ultralytics import YOLO
import paho.mqtt as mqtt
from paho.mqtt import client as _
from threading import Thread
import time
import datetime

class Controller:
    def __init__(self):
        self.yolo = YOLO("model/yolov8n.pt")
        self.mqtt = mqtt.client.Client(mqtt.client.CallbackAPIVersion.VERSION2, client_id='controller')
        self.mqtt.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        
        self.devices = set()
        self.authorized = set()

        self.triggered = False
        self.armed = False

        def on_connect(client, userdata, flags, reason_code, properties):
            client.subscribe('image/submit')
            client.subscribe('image/request')
            client.subscribe('device/online')
            client.subscribe('device/offline')
            client.subscribe('alarm/disarm')
            client.subscribe('alarm/defuse')
            client.subscribe('alarm/rearm')
        self.mqtt.on_connect = on_connect

    def detect_cat(self, file_path) -> bool:
        result = self.yolo.predict(file_path)[0]

        for box in result.boxes:
            confidence = round(box.conf[0].item(), 3)
            obj = result.names[box.cls[0].item()]
            if obj == 'person' and confidence > 0.75:
                self.mqtt.publish('alarm/sound', payload=None, qos=1)
                return False
            elif obj == 'cat' or obj == 'dog' and confidence > 0.75:
                print(f'false alarm, it was a {obj}\t(I\'m {confidence*100}% sure)')
                return True
    
        print('no cat detected')
        return False
    
    def start(user, password, host, port):
        time.sleep(10)
        controller = Controller()
        controller.mqtt.username_pw_set(user, password)

        def on_message(client, userdata, msg):
            match msg.topic:

                case 'device/online':
                    controller.devices.add(str(msg.payload))
                    print(f'DEVICE ONLINE: {msg.payload}')
                    for id in controller.authorized:
                        controller.mqtt.publish('device/ack', payload=f'{msg.payload}+{id}', qos=1)
                    if controller.armed:
                        controller.mqtt.publish('alarm/rearm', payload=msg.payload, qos=1)

                case 'device/offline':
                    print(f'DEVICE OFFLINE: {msg.payload}')
                    if controller.armed:
                        controller.triggered = True
                        def timer_callback(device=None):
                            for i in range(20):
                                time.sleep(1)
                            if controller.triggered:
                                controller.mqtt.publish('alarm/sound', payload=None, qos=1)
                                print('ALARM SOUND')
                        timer = Thread(target=timer_callback, kwargs={'device': str(msg.payload)})
                        timer.start()
                    else:
                        controller.devices.remove(msg.payload)
                        
                case 'image/submit':
                    print('IMAGE RECEIVED')
                    file_path = f'/images/{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:&S")}'
                    with open(file_path, 'wb') as file:
                        file.write(msg.payload)
                        if controller.detect_cat(file_path):
                            controller.triggered = False
                            controller.mqtt.publish('alarm/defuse', payload=msg.payload, qos=1)

                case 'image/request':
                    print('IMAGE REQUESTED')
                    controller.triggered = True
                    def timer_callback(device=None):
                        for i in range(20):
                            time.sleep(1)
                        if controller.triggered:
                            controller.mqtt.publish('alarm/sound', payload=device, qos=1)
                    timer = Thread(target=timer_callback, kwargs={'device': str(msg.payload)})
                    timer.start()

                case 'alarm/disarm':
                    print('ALARM DISARMED')
                    controller.armed = False
                    controller.triggered = False

                case 'alarm/defuse':
                    print('ALARM DEFUSED')
                    controller.triggered = False

                case 'alarm/rearm':
                    print('ALARM REARMED')
                    controller.armed = True

        controller.mqtt.on_message = on_message
        controller.mqtt.connect(host, port, 60)
        controller.mqtt.loop_forever()

if __name__ == '__main__':
    from os import getenv
    from dotenv import load_dotenv
    load_dotenv()
    Controller.start(user=getenv('MQTT_USER'),
                     password=getenv('MQTT_PASSWORD'),
                     host=getenv('MQTT_HOST'),
                     port= int(getenv('MQTT_PORT')),)
