import http.server

# wrapper for the python standard library web server implementation
class Server(http.server.SimpleHTTPRequestHandler):
    def __init__(self, host='', port=8080):
        server_address = (host, port)
        self.inner = http.server.HTTPServer(server_address, Server)

    # defines existing routes
    def do_GET(self):
        if self.path == '/script.js' or self.path == '/style.css':
            self.path = f'static{self.path}'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif self.path == '/favicon.ico':
            self.path = 'static/icon.png'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        elif self.path == '/':
            self.path = 'static/index.html'
            return http.server.SimpleHTTPRequestHandler.do_GET(self)
        else:
            self.send_error(404, f"{self.path} is not on this server, sorry!")
    
    def serve_forever(self):
        self.inner.serve_forever()

    def start(host='', port=8080):
        server = Server(host, port)
        server.serve_forever()