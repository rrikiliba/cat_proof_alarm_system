#!/usr/bin/env python3
from ultralytics import YOLO
import paho.mqtt as mqtt
from paho.mqtt import client as _
from threading import Thread
import time
import datetime

class Controller:
    def __init__(self):
        print(' * Loading YOLO model')
        # load the YOLOv8 pre-trained model
        self.yolo = YOLO("model/yolov8n.pt")
        # connect to mqtt
        self.mqtt = mqtt.client.Client(mqtt.client.CallbackAPIVersion.VERSION2, client_id='controller')
        # during testing we used a cloud based broker that required TLS
        # self.mqtt.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        
        # set of currently connected devices
        self.devices = set()

        # set of RFID keys authorized to defeuse the alarm
        self.authorized = set()

        # states for the controller
        self.triggered = False
        self.armed = False

        # subscribe to topics on connect
        # so that subscriptions don't get lost in case of reconnection
        def on_connect(client, userdata, flags, reason_code, properties):
            print(' * MQTT client connected')
            client.subscribe('image/submit')
            client.subscribe('image/request')
            client.subscribe('device/online')
            client.subscribe('device/offline')
            client.subscribe('alarm/disarm')
            client.subscribe('alarm/rearm')
        self.mqtt.on_connect = on_connect


    # detects a cat in the image with the given file path
    # will return True if the confidence of cat or dog detection
    # is above a certain treshold (75%)
    def detect_cat(self, file_path: str) -> bool:
        result = self.yolo.predict(file_path)[0]

        for box in result.boxes:
            confidence = round(box.conf[0].item(), 3)
            obj = result.names[box.cls[0].item()]
            # if obj == 'person' and confidence > 0.75:
            #     self.mqtt.publish('alarm/sound', payload=None, qos=1)
            #     return False
            if obj == 'cat' or obj == 'dog' and confidence > 0.75:
                print(f'False alarm, it was a {obj}\t(I\'m {confidence*100}% sure)')
                return True
    
        print('No cat detected')
        return False
    
    def start(user, password, host, port):
        print(' * Starting MQTT client')
        controller = Controller()
        #controller.mqtt.username_pw_set(user, password)

        # callback for mqtt message reception
        def on_message(client, userdata, msg):
            match msg.topic:

                # in case a new device comes online
                case 'device/online':
                    
                    # save it to the online devices
                    controller.devices.add(str(msg.payload))
                    
                    # log the  event
                    print(f'DEVICE ONLINE: {msg.payload}')

                    # if the device is not in the list, it is newly connected
                    if msg.payload not in controller.devices:
                        
                        # send the list of authorized keys to the new device
                        for id in controller.authorized:
                            controller.mqtt.publish(f'device/ack/{msg.payload}', payload=f'{id}', qos=1)

                        # attempt to rearm the new device                    
                        if controller.armed:
                            controller.mqtt.publish(f'alarm/rearm/{msg.payload}', None, qos=1)
                    
                    # if the device was already in the list, it was disconnected abruptly,
                    # but it has now reconnected, so defuse the alarm internally
                    else:
                        controller.triggered = False

                # in case a device goes offline
                case 'device/offline':

                    # log the event
                    print(f'DEVICE OFFLINE: {msg.payload}')

                    # take action if the device is brought offline
                    # while the system is armed
                    if controller.armed:

                        # consider the alarm triggered
                        controller.triggered = True

                        # start a 20 second timer before sounding the alarm
                        # so that the device has time to reconnect
                        # or the user has time to disarm manually
                        def timer_callback(device=None):
                            for i in range(20):
                                time.sleep(1)
                            if controller.triggered:
                                controller.devices.discard(device)
                                controller.mqtt.publish('alarm/sound', payload=None, qos=1)
                                print('ALARM SOUND')
                        timer = Thread(target=timer_callback, kwargs={'device': str(msg.payload)})
                        timer.start()
                    else:
                        controller.devices.remove(msg.payload)
                        
                # in case an image is submitted to for inference
                case 'image/submit':

                    # log the event
                    print('Image received')

                    # save the image to file
                    file_path = f'images/{datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")}.jpeg'
                    with open(file_path, 'wb') as file:
                        file.write(msg.payload)

                        # defuse the alarm if cat detected
                        if controller.detect_cat(file_path):
                            controller.triggered = False
                        else :
                            print('N')
                
                # in case an image is requested (which means a motion sensor was activated)
                case 'image/request':

                    # log the event
                    print('Image requested')

                    # start a 20 second timer before sounding the alarm
                    # so that there is time to use the RFID to disarm the system
                    # and to perform inference to check if a cat is in the image
                    controller.triggered = True
                    def timer_callback(device=None):
                        for i in range(20):
                            time.sleep(1)
                        if controller.triggered:
                            controller.mqtt.publish('alarm/sound', payload=device, qos=1)
                    timer = Thread(target=timer_callback, kwargs={'device': str(msg.payload)})
                    timer.start()

                # in case the alarm needs to be disarmed
                case 'alarm/disarm':
                    print('Alarm disarmed')
                    controller.armed = False
                    controller.triggered = False

                # in case the alarm needs to be rearmed
                case 'alarm/rearm':
                    print('Alarm rearmed')
                    controller.armed = True

        controller.mqtt.on_message = on_message
        controller.mqtt.connect(host, port, 60)

        print(' * Now running')
        controller.mqtt.loop_forever()

if __name__ == '__main__':
    from os import getenv
    Controller.start(user=getenv('MQTT_USER'),
                     password=getenv('MQTT_PASSWORD'),
                     host=getenv('MQTT_HOST'),
                     port= int(getenv('MQTT_PORT')),)
