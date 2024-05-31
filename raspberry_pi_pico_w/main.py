import network
from umqtt.simple import MQTTClient

from mfrc522 import MFRC522

import utime
import machine
from machine import Pin

import secrets as cfg

# connect to wifi
wlan = network.WLAN()
wlan.active(True)
while not wlan.isconnected():
    print('WIFI CONNECTING')
    wlan.connect(cfg.WIFI_SSID, cfg.WIFI_PASSWORD)
    utime.sleep_ms(1000)
print('WIFI OK')
 

class Alarm:
    def __init__(self):
        # initialise all peripherals
        self.peripherals = {
            'RFID': MFRC522(rst=15,sck=10,cs=13,miso=12,mosi=11,spi_id=1),
            'MOTION': Pin(14,Pin.IN,Pin.PULL_DOWN),
            'BUZZER': Pin(0,Pin.OUT)
            }
        
        # set the device as unarmed
        self.armed = False
        
        # keep trying to connect to mqtt indefinitely
        mqtt_ok = False
        while not mqtt_ok:
            try:
                self.mqtt = MQTTClient(client_id=cfg.DEVICE_ID,
                                        server=cfg.MQTT_BROKER,
                                        port=cfg.MQTT_PORT,
                                        user=cfg.MQTT_USER,
                                        password=cfg.MQTT_PASSWORD,
                                        keepalive=60,
                                        ssl=cfg.MQTT_SSL,
                                        ssl_params=cfg.MQTT_SSL_PARAMS)
                self.mqtt.set_callback(self.recv_msg)
                self.mqtt.connect()
                mqtt_ok = True
            except OSError as e:
                print('MQTT CONNECTING')
                
        # subscribe to relevant topics
        self.mqtt.subscribe(b'device/ack/'+cfg.DEVICE_ID)
        self.mqtt.subscribe(b'alarm/disarm')
        self.mqtt.subscribe(b'alarm/rearm')
        self.mqtt.subscribe(b'alarm/sound')

        self.mqtt.publish(b'device/online', cfg.DEVICE_ID)
        self.mqtt.set_last_will(b'device/offline', cfg.DEVICE_ID)
        print('MQTT OK')

    # defines the interrupt for the motion sensor and arms the alarm
    def rearm(self):
        self.peripherals['MOTION'].irq(trigger=Pin.IRQ_RISING, handler=self.motion_triggered)
        self.armed = True
        print('ARMED')
        self.peripherals['BUZZER'].value(1)
        utime.sleep_ms(600)
        self.peripherals['BUZZER'].value(0)

    # clears the interrupt for the motion sensor and disarms the alarm
    def disarm(self):
        self.peripherals['MOTION'].irq(handler=None)
        self.armed = False
        print('DISARMED')
        self.peripherals['BUZZER'].value(1)
        utime.sleep_ms(200)
        self.peripherals['BUZZER'].value(0)
        utime.sleep_ms(200)
               
    # sounds the device's buzzer
    def sound(self):
        print('SOUND')
        if self.armed:
            for _ in range(10):
                if not self.armed:
                    break
                self.peripherals['BUZZER'].value(1)
                utime.sleep_ms(1000)
                self.peripherals['BUZZER'].value(0)
                utime.sleep_ms(500)

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
                        self.mqtt.publish(b'alarm/disarm', cfg.DEVICE_ID)
                        self.disarm()

                    # otherwise, the card is invalid;
                    # give a small timeout and notify the user
                    else:
                        print('AUTH FAIL')
                        utime.sleep_ms(1000)
                        for _ in range(3):
                            self.peripherals['BUZZER'].value(1)
                            utime.sleep_ms(200)
                            self.peripherals['BUZZER'].value(0)
                            utime.sleep_ms(200)
            self.mqtt.check_msg()
            utime.sleep_ms(100)

    # callback for the interrupt
    def motion_triggered(self, _):
        if self.armed:
            self.mqtt.publish(b'image/request', cfg.CAM_ID)
            print('MOVEMENT DETECTED!')
            self.poll_card()

    # callback for the mqtt client
    def recv_msg(self, topic, msg):
        if topic == b'device/ack/'+cfg.DEVICE_ID:
            try:
                new_RFID = int.from_bytes(bytes(msg), 'little', False)
                cfg.RFID_AUTHORIZED.append(new_RFID)
            except:
                pass
        elif topic == b'alarm/disarm':
            self.disarm()
        elif topic == b'alarm/rearm':
            self.rearm()
        elif topic == b'alarm/sound':
            self.sound()
            
                  
            
if __name__ == '__main__':
    alarm = Alarm()
    print('BOOT OK')
    while True:
        if not alarm.armed:
            # if the alarm is not armed, we can use a blocking function to wait
            # for the rearm message
            alarm.mqtt.wait_msg()
        else:
            # otherwise we unfortunately have to poll for new mqtt messages
            # because the blocking `wait_msg` also prevents the interrupt from the movement sensor
            alarm.mqtt.check_msg()
            utime.sleep_ms(100)