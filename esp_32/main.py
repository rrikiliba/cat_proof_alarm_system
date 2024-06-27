import network
import camera
import utime
from umqtt.simple import MQTTClient
import secrets as cfg

# connect to wifi
def connect_to_wifi():
    wlan = network.WLAN()
    wlan.active(True)
    while not wlan.isconnected():
        print('WIFI CONNECTING')
        wlan.connect(cfg.WIFI_SSID, cfg.WIFI_PASSWORD)
        utime.sleep_ms(1000)
    print('WIFI OK')
    return wlan

# connect to mqtt
def connect_to_mqtt():

    def recv_msg(topic, msg):
        if msg.decode('ASCII') == cfg.DEVICE_ID:
            print('IMG REQ')
            try:
                camera.init(0, format=camera.JPEG, fb_location=camera.PSRAM, xclk_freq=camera.XCLK_10MHz)
                print('CAM OK')
                camera.flip(1)
                buf = camera.capture()
                mqtt.publish('image/submit', buf)
                print('IMG SENT')
            except:
                print('CAM ERR')
            finally:
                camera.deinit()

    while True:
        try:
            mqtt = MQTTClient(client_id=cfg.DEVICE_ID,
                    server=cfg.MQTT_BROKER,
                    port=cfg.MQTT_PORT,
                    user=cfg.MQTT_USER,
                    password=cfg.MQTT_PASSWORD,
                    keepalive=120,
                    #ssl=cfg.MQTT_SSL,
                    #ssl_params=cfg.MQTT_SSL_PARAMS
                    )
            mqtt.set_callback(recv_msg)
            mqtt.connect()
            # subscribe to relevant topics
            mqtt.subscribe('image/request')
            mqtt.publish('device/online', cfg.DEVICE_ID)
            mqtt.set_last_will('device/offline', cfg.DEVICE_ID)
            print('MQTT OK')
            return mqtt
        except OSError as e:
            print('MQTT CONNECTING')
            utime.sleep_ms(1000)

if __name__ == '__main__':
    conn = connect_to_wifi()
    mqtt = connect_to_mqtt()
    print('BOOT OK')
    while True:
        try:
            mqtt.wait_msg()
        except:
            print('CONN LOST')
            conn = connect_to_wifi()
            mqtt = connect_to_mqtt()