import network
import camera
import utime
import machine
from umqtt.simple import MQTTClient
import secrets as cfg

# connect to wifi
wlan = network.WLAN()
wlan.active(True)
while not wlan.isconnected():
    print('WIFI CONNECTING')
    wlan.connect(cfg.WIFI_SSID, cfg.WIFI_PASSWORD)
    utime.sleep_ms(1000)
print('WIFI OK')

camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM)
def recv_msg(topic, msg):
    if msg == cfg.DEVICE_ID:
        print('IMG REQ')
        buf = camera.capture()
        mqtt.publish(b'image/submit', buf)

# keep trying to connect to mqtt indefinitely
mqtt_ok = False
while not mqtt_ok:
    try:
        mqtt = MQTTClient(client_id=cfg.DEVICE_ID,
                            server=cfg.MQTT_BROKER,
                            port=cfg.MQTT_PORT,
                            #user=cfg.MQTT_USER,
                            #password=cfg.MQTT_PASSWORD,
                            keepalive=60,
                            #ssl=cfg.MQTT_SSL,
                            #ssl_params=cfg.MQTT_SSL_PARAMS
                          )
        mqtt.set_callback(recv_msg)
        mqtt.connect()
        mqtt_ok = True
    except OSError as e:
        print('MQTT CONNECTING')
                
# subscribe to relevant topics
mqtt.subscribe(b'image/request')
print('MQTT OK')

if __name__ == '__main__':
    print('BOOT OK')
    while True:
        mqtt.check_msg()
        utime.sleep_ms(100)
