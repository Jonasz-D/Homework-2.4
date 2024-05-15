from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse, mimetypes, pathlib, socket, json, threading
from datetime import datetime

import os
os.chdir(r'C:\Users\jp120\Desktop\Projects-Git\module_2\Homework-2.4\Homework-2.4\front-init')
print(os.getcwd())

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message':
            self.send_html_file('message.html')
        else:
            if pathlib.Path().joinpath(pr_url.path[1:]).exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'.{self.path}', 'rb') as file:
            self.wfile.write(file.read())

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        data_parse = urllib.parse.unquote_plus(data.decode())
        data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
        run_udp_client(UDP_IP, UDP_PORT, data_dict)
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()


def update_json_file(data):
    with open(r'storage/data.json', 'r+') as f:
        key = str(datetime.now())
        value = data
        json_data = json.load(f)
        json_data[key] = value
        f.seek(0)
        json.dump(json_data, f) 


def run_udp_server(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    sock.bind(server)
    try:
        while True:
            data, address = sock.recvfrom(1024)
            data.decode()
            data = json.loads(data)
            print(f'Received data: {data} from: {address}')
            update_json_file(data)

    except KeyboardInterrupt:
        print(f'Destroy server')
    finally:
        sock.close()

def run_udp_client(ip, port, data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = ip, port
    data = json.dumps(data)
    data = data.encode()
    sock.sendto(data, server)
    print(f'Send data to server: {server}')
    sock.close()


def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_http_address = ('', 3000)
    http = server_class(server_http_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()

UDP_IP = '127.0.0.1'
UDP_PORT = 5000

if __name__ == '__main__':
    server_http = threading.Thread(target=run)
    server_udp = threading.Thread(target=run_udp_server, args=(UDP_IP, UDP_PORT))
    server_http.start()
    server_udp.start()
    server_http.join()
    server_udp.join()

