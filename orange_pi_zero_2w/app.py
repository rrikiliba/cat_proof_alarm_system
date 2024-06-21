from threading import Thread
from controller import Controller
import os
from dotenv import load_dotenv
import http.server

class Server(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/script.js' or self.path == '/style.css':
            self.path = f'static{self.path}'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif self.path == '/':
            self.path = 'static/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_error(404, "Not on this server, sorry!")
    
load_dotenv()

Thread(target=Controller.start, 
       kwargs={'user':os.getenv('MQTT_USER'), 
               'password': os.getenv('MQTT_PASSWORD'),
               'host': os.getenv('MQTT_HOST'),
               'port': int(os.getenv('MQTT_PORT')),
               }).start()

port = int(os.getenv('HTTP_PORT'))
server_address = ('', port)
httpd = http.server.HTTPServer(server_address, Server)
print(f' * Server running on port {port}')
httpd.serve_forever()