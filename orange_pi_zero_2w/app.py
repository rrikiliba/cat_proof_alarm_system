from threading import Thread
from controller import Controller
from server import Server
from os import getenv as env 
from dotenv import load_dotenv as dotenv

# load the variables contained in .env into the environment
dotenv()

# setup secondary thread
controller_thread = Thread(target=Controller.start, 
        kwargs={'user':env('MQTT_USER'), 
                'password': env('MQTT_PASSWORD'),
                'host': env('MQTT_HOST'),
                'port': int(env('MQTT_PORT')),
                }
        )

# start both tasks
controller_thread.start()
Server.start(port=int(env("HTTP_PORT")))