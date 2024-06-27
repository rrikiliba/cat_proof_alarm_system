from ultralytics import YOLO
import paho.mqtt as mqtt
from paho.mqtt import client as _
import luma.oled as oled
from luma.core.interface.serial import i2c
from luma.oled.device import ssd1306
from os import getenv as env
from threading import Thread
import time
import datetime

class Controller:

    # constructor
    def __init__(self):
        self.log('Loading YOLO model', start='*')
        # load the YOLOv8 pre-trained model
        self.yolo = YOLO("model/yolov8n.pt")
        # connect to mqtt
        self.mqtt = mqtt.client.Client(mqtt.client.CallbackAPIVersion.VERSION2, client_id='controller')
        
        # during the first stages of testing, we used a cloud based broker that required TLS
        # self.mqtt.tls_set(tls_version=mqtt.client.ssl.PROTOCOL_TLS)
        
        # attempt to initialize the ssd1306 OLED device that communicates via I²C
        try:
            serial = i2c(port=1, address=int(env('I2C_ADDR'), 16))
            self.screen = ssd1306(serial)
        except Exception as e:
            self.log(e, start='!', oled=False)
        self.log(f'Screen connected: {hasattr(self, "screen")}', start='*', oled=False)

        # set of currently connected devices
        # they each add themselves here by sending a message to device/online with their ID
        self.devices = set()

        # set of RFID keys authorized to defeuse the alarm
        self.log('Loading authorized file', start='*')
        self.authorized = set()
        # attempt to read all the entries in the file containing the keys' ids
        with open('.authfile') as file:
            count = 0
            for line in file:
                try: 
                    # each line contains exactly one entry
                    self.authorized.add(int(line.rstrip()))
                    count = count + 1
                except:
                    # signal possible errors (couldn't parse int)
                    self.log(f'Found malformed entry at line {count}', start='!')
            self.log(f'Loaded {count} entries', start='*')

        # states for the controller
        self.triggered = False
        self.armed = False

        # subscribe to topics on connect
        # so that subscriptions don't get lost in case of reconnection
        def on_connect(client, userdata, flags, reason_code, properties):
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
                self.log(f'{obj} detected at {confidence*100}%, defused')
                return True
    
        self.log('No cat or dog detected', start='!')
        return False
    
    # custom logging function that will attempt to write the passed message both to stdout and to the OLED device, if present
    def log(self, msg, start='>', timestamp=None, use_timestamp=True, stdout=True, oled=True):
        if use_timestamp and timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        elif not use_timestamp and timestamp is not None:
            timestamp = None

        # formatted message
        msg = f'{timestamp} {start} {msg}'
        if oled and hasattr(self, 'screen'):
            with oled.render.canvas(self.screen) as draw:
                draw.rectangle(self.screen.bounding_box, outline="white", fill="black")
                draw.text((30, 40), msg, fill="white")
        if stdout:
            print(msg) 


    # constructs a Controller instance and loops forever
    def start(user, password, host, port):
        controller = Controller()
        controller.log('Starting MQTT client', start='*')

        # callback for mqtt message reception
        def on_message(client, userdata, msg):
            match msg.topic:
                # in case a new device comes online
                case 'device/online':
                    device_name = msg.payload.decode('ASCII')
                    # log the  event
                    controller.log(f'Device online: {device_name}')
                    
                    if device_name == 'webapp':
                        controller.mqtt.publish(f'device/ack/webapp', payload='1' if controller.armed else '0', qos=1)
                    else: 
                        # if the device is not in the list, it is newly connected
                        if device_name not in controller.devices:
                            
                             # save its id (sent in the msg payload) to the online devices
                            controller.devices.add(device_name)

                            # send the list of authorized keys to the new device
                            for id in controller.authorized:
                                controller.mqtt.publish(f'device/ack/{device_name}', payload=id.to_bytes(4, byteorder="little"), qos=1)

                            # attempt to rearm the new device                    
                            if controller.armed:
                                controller.mqtt.publish(f'alarm/rearm/{device_name}', None, qos=1)
                        
                        # if the device was already in the list, it was disconnected abruptly,
                        # but it has now reconnected, so defuse the alarm internally
                        else:
                            controller.triggered = False

                # in case a device goes offline
                case 'device/offline':
                    # log the event
                    controller.log(f'Device offline: {msg.payload.decode("ASCII")}', start='!')

                    # take action if the device is brought offline
                    # while the system is armed
                    if controller.armed:

                        # consider the alarm triggered
                        controller.triggered = True

                        # start a 20 second timer before sounding the alarm
                        # so that the device has time to reconnect
                        # or the user has time to disarm manually
                        def timer_callback(device=None):
                            for i in range(20, 0, -1):
                                controller.log(f"Time left: {i}", stdout=False)
                                time.sleep(1)
                            if controller.triggered:
                                controller.devices.discard(device)
                                controller.mqtt.publish('alarm/sound', payload=None, qos=1)
                                controller.log('Alarm sound', start='!')
                        timer = Thread(target=timer_callback, kwargs={'device': msg.payload.decode('ASCII')})
                        timer.start()
                    else:
                        controller.devices.discard(msg.payload.decode('ASCII'))
                        
                # in case an image is submitted to for inference
                case 'image/submit':
                    timestamp = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")

                    # log the event
                    controller.log(f'Image received', timestamp=timestamp)

                    # save the image to file
                    file_path = f'images/{timestamp}.jpeg'
                    with open(file_path, 'wb') as file:
                        file.write(msg.payload)

                        # defuse the alarm if cat detected
                        if controller.detect_cat(file_path):
                            controller.triggered = False
                
                # in case an image is requested (which means a motion sensor was activated)
                case 'image/request':
                    # log the event
                    controller.log(f'Image requested')

                    if controller.armed:
                        # put the alarm in the 'triggered' state
                        controller.triggered = True
                        
                        # start a 20 second timer before sounding the alarm
                        # so that there is time to use the RFID to disarm the system
                        # and to perform inference to check if a cat is in the image
                        def timer_callback(device=None):
                            for i in range(20, 0, -1):
                                controller.log(f"Time left: {i}", stdout=False)
                                time.sleep(1)
                            if controller.triggered:
                                controller.devices.discard(device)
                                controller.mqtt.publish('alarm/sound', payload=None, qos=1)
                                controller.log('Alarm sound', start='!')
                        timer = Thread(target=timer_callback, kwargs={'device': msg.payload.decode('ASCII')})
                        timer.start()

                # in case the alarm needs to be disarmed
                case 'alarm/disarm':
                    #set the screen text
                    controller.log("System is disarmed")
                    controller.armed = False
                    controller.triggered = False

                # in case the alarm needs to be rearmed
                case 'alarm/rearm':
                    #set the screen text
                    controller.log("System is armed")
                    controller.armed = True

        controller.mqtt.on_message = on_message
        controller.mqtt.username_pw_set(username=user, password=password)
        controller.mqtt.connect(host, port, 60)

        controller.log('Controller running', start='*')
        controller.mqtt.loop_forever()

if __name__ == '__main__':
    Controller.start(user=env('MQTT_USER'),
                     password=env('MQTT_PASSWORD'),
                     host=env('MQTT_HOST'),
                     port= int(env('MQTT_PORT')),
                    )