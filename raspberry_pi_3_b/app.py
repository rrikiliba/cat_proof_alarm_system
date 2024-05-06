from flask import Flask
from flask_cors import CORS

from threading import Thread

from controller import Controller

from os import getenv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app=app)

@app.route('/')
def homepage():
    return app.send_static_file('index.html')
    
Thread(target=Controller.start, 
       kwargs={'user':getenv('MQTT_USER'), 
               'password': getenv('MQTT_PASSWORD'),
               'host': getenv('MQTT_HOST'),
               'port': int(getenv('MQTT_PORT')),
               }).start()
app.run(getenv('HTTP_HOST'),getenv('HTTP_PORT'),True,False)