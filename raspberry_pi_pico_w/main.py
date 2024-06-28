import network
from umqtt.simple import MQTTClient

from mfrc522 import MFRC522

import utime
from machine import Pin

import secrets as cfg
 
class Alarm:
    def __init__(self):
        # initialise all peripherals
        self.peripherals = {
            'RFID': MFRC522(rst=15,sck=10,cs=13,miso=12,mosi=11,spi_id=1),
            'MOTION': Pin(14,Pin.IN,Pin.PULL_DOWN),
            'BUZZER': Pin(0,Pin.OUT),
            'LED': Pin('LED', Pin.OUT)
            }
        
        # set the device as unarmed
        self.armed = False

        self.connect_to_wifi()
        self.connect_to_mqtt()
                
    # connect to wifi
    def connect_to_wifi(self):
        self.wlan = network.WLAN()
        self.wlan.active(True)
        while not self.wlan.isconnected():
            print('WIFI CONNECTING')
            try:
                self.wlan.connect(cfg.WIFI_SSID, cfg.WIFI_PASSWORD)
            except:
                utime.sleep_ms(1000)
        print('WIFI OK')

    # connect to mqtt
    def connect_to_mqtt(self):
        while True:
            try:
                self.mqtt = MQTTClient(client_id=cfg.DEVICE_ID,
                    server=cfg.MQTT_BROKER,
                    port=cfg.MQTT_PORT,
                    user=cfg.MQTT_USER,
                    password=cfg.MQTT_PASSWORD,
                    keepalive=120,
                    #ssl=cfg.MQTT_SSL,
                    #ssl_params=cfg.MQTT_SSL_PARAMS
                    )
                self.mqtt.set_callback(self.recv_msg)
                self.mqtt.set_last_will('device/offline', cfg.DEVICE_ID)
        
                self.mqtt.connect()
        
                # subscribe to relevant topics
                self.mqtt.subscribe('device/ack/'+cfg.DEVICE_ID)
                self.mqtt.subscribe('alarm/disarm')
                self.mqtt.subscribe('alarm/rearm')
                self.mqtt.subscribe('alarm/rearm/'+cfg.DEVICE_ID)
                self.mqtt.subscribe('alarm/sound')

                self.mqtt.publish('device/online', cfg.DEVICE_ID)
                print('MQTT OK')
                return
            except OSError as e:
                print('MQTT CONNECTING')
                utime.sleep_ms(1000)

    # defines the interrupt for the motion sensor and arms the alarm
    def rearm(self):
        self.peripherals['LED'].value(1)
        print('ARMED')
        self.peripherals['BUZZER'].value(1)
        utime.sleep_ms(600)
        self.peripherals['BUZZER'].value(0)
        self.armed = True
        self.peripherals['MOTION'].irq(trigger=Pin.IRQ_RISING, handler=self.motion_triggered)

    # clears the interrupt for the motion sensor and disarms the alarm
    def disarm(self):
        self.peripherals['MOTION'].irq(handler=None)
        self.armed = False
        self.peripherals['LED'].value(0)
        print('DISARMED')
        self.peripherals['BUZZER'].value(1)
        utime.sleep_ms(200)
        self.peripherals['BUZZER'].value(0)
        utime.sleep_ms(200)
               
    # sounds the device's buzzer
    def sound(self):
        if self.armed:
            print('SOUND')
            for _ in range(10):
                if not self.armed:
                    break
                self.peripherals['BUZZER'].value(1)
                utime.sleep_ms(1000)
                self.peripherals['BUZZER'].value(0)
                utime.sleep_ms(500)
                try:
                    alarm.mqtt.check_msg()
                except:
                    pass
            self.disarm()

    # starts polling the RFID reader
    def poll_card(self):
        while self.armed:
            
            # we use a *very* small subset of functionalities from the RFID sensor driver
            self.peripherals['RFID'].init()
            (status, _) = self.peripherals['RFID'].request(self.peripherals['RFID'].REQIDL)
            if status == self.peripherals['RFID'].OK:

                # if the sensor is ready, attempt to read RFID card
                (status, uid) = self.peripherals['RFID'].SelectTagSN()
                if status == self.peripherals['RFID'].OK:

                    # if status indicates success, parse numeric uid from card
                    print('CARD SCANNED')
                    card = int.from_bytes(bytes(uid), 'little', False)

                    # if the uid denotes a card which is authorized to defuse the alarm, do so
                    if card in cfg.RFID_AUTHORIZED:
                        print('AUTH OK')
                        self.mqtt.publish('alarm/disarm', cfg.DEVICE_ID)
                        self.disarm()

                    # otherwise, the card is invalid
                    # give a small timeout and notify the user
                    else:
                        print('AUTH FAIL')
                        utime.sleep_ms(1000)
                        for _ in range(3):
                            self.peripherals['BUZZER'].value(1)
                            utime.sleep_ms(200)
                            self.peripherals['BUZZER'].value(0)
                            utime.sleep_ms(200)
            try:
                self.mqtt.check_msg()
                utime.sleep_ms(100)
            except:
                print('CONN LOST')
                alarm.connect_to_wifi()
                alarm.connect_to_mqtt()

    # callback for the interrupt
    def motion_triggered(self, _):
        if self.armed:
            self.mqtt.publish('image/request', cfg.CAM_ID)
            print('MOVEMENT DETECTED!')
            self.poll_card()

    # callback for the mqtt client
    def recv_msg(self, topic, msg):
        # print('MSG ON '+topic.decode('ASCII'))
        ack_topic = 'device/ack/'+cfg.DEVICE_ID
        rearm_topic = 'alarm/rearm/'+cfg.DEVICE_ID
        if topic == ack_topic.encode('ASCII') or topic == ack_topic.encode('utf-8'):
            try:
                new_RFID = int.from_bytes(bytes(msg), 'little', False)
                cfg.RFID_AUTHORIZED.append(new_RFID)
                print('AUTH ADD')
            except:
                pass
        elif topic == b'alarm/disarm':
            self.disarm()
        elif topic == b'alarm/rearm' or topic == rearm_topic.encode('ASCII') or topic == rearm_topic.encode('utf-8'):
            self.rearm()
        elif topic == b'alarm/sound':
            self.sound()
            
                  
            
if __name__ == '__main__':
    alarm = Alarm()
    print('BOOT OK')
    while True:
        try:
            alarm.mqtt.check_msg()
            utime.sleep_ms(100)
        except:
            print('CONN LOST')
            alarm.connect_to_wifi()
            alarm.connect_to_mqtt()