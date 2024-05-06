import network
from umqtt.simple import MQTTClient

from mfrc522 import MFRC522

import utime
import machine
from machine import Pin

import secrets as cfg

wlan = network.WLAN()
wlan.active(True)
while not wlan.isconnected():
    print('WIFI CONNECTING')
    wlan.connect(cfg.WIFI_SSID, cfg.WIFI_PASSWORD)
    utime.sleep_ms(1000)
print('WIFI OK')
 

class Alarm:
    def __init__(self):
        self.peripherals = {
            'RFID': MFRC522(rst=15,sck=10,cs=13,miso=12,mosi=11,spi_id=1),
            'MOTION': Pin(14,Pin.IN,Pin.PULL_DOWN),
            'BUZZER': Pin(0,Pin.OUT)
            }
        self.armed = False
        
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
                
        self.mqtt.subscribe(b'device/ack')
        self.mqtt.subscribe(b'alarm/disarm')
        self.mqtt.subscribe(b'alarm/rearm')
        self.mqtt.publish(b'device/online', cfg.DEVICE_ID)
        self.mqtt.set_last_will(b'device/offline', cfg.DEVICE_ID)
        print('MQTT OK')

    def rearm(self):
        self.peripherals['MOTION'].irq(trigger=Pin.IRQ_RISING, handler=self.motion_triggered)
        self.armed = True
        print('ARMED')

    def disarm(self):
        self.peripherals['MOTION'].irq(handler=None)
        self.armed = False
        print('DISARMED')
               
    def sound(self):
        print('SOUND')
        if self.armed:
            for _ in range(5):
                self.peripherals['BUZZER'].value(1)
                utime.sleep_ms(1000)
                self.peripherals['BUZZER'].value(0)
                utime.sleep_ms(500)

    def poll_card(self):
        while self.armed:
            self.peripherals['RFID'].init()
            (stat, tag_type) = self.peripherals['RFID'].request(self.peripherals['RFID'].REQIDL)
            if stat == self.peripherals['RFID'].OK:
                (stat, uid) = self.peripherals['RFID'].SelectTagSN()
                if stat == self.peripherals['RFID'].OK:
                    print('CARD SCANNED')
                    card = int.from_bytes(bytes(uid), 'little', False)
                    if card in cfg.RFID_AUTHORIZED:
                        print('AUTH OK')
                        self.mqtt.publish(b'alarm/disarm', cfg.DEVICE_ID)
                        self.disarm()
                    else:
                        print('AUTH FAIL')
                        utime.sleep_ms(3000)
            utime.sleep_ms(100)

    def motion_triggered(self, _):
        if self.armed:
            self.mqtt.publish(b'image/request', cfg.DEVICE_ID)
            print('MOVEMENT DETECTED!')
            self.poll_card()

    def recv_msg(self, topic, msg):
        if topic == b'device/ack':
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
            alarm.mqtt.wait_msg()
        else:
            alarm.mqtt.check_msg()