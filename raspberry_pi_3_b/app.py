#!/usr/bin/env python3
from threading import Thread
from controller import Controller
import os
from dotenv import load_dotenv
import http.server

class Server(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/':
            if self.path == '/':
                self.path = 'static/index.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    
load_dotenv()

Thread(target=Controller.start, 
       kwargs={'user':os.getenv('MQTT_USER'), 
               'password': os.getenv('MQTT_PASSWORD'),
               'host': os.getenv('MQTT_HOST'),
               'port': int(os.getenv('MQTT_PORT')),
               }).start()

server_address = ('', 5000)
httpd = http.server.HTTPServer(server_address, Server)
print(' * Server running on port 5000')
httpd.serve_forever()