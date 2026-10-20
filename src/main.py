from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import pathlib
import mimetypes
import threading
import socket
import json
import logging

HTTP_PORT = 3000
HTTP_HOST = '0.0.0.0'
SOCKET_PORT = 5000
SOCKET_HOST = '127.0.0.1'
BUFFER_SIZE = 1024

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('templates/index.html')
        elif pr_url.path == '/message':
            self.send_html_file('templates/message.html')
        else:
            if pr_url.path.split('.')[-1] not in ['html', 'js'] and "." in pr_url.path:
                self.send_static()
            else:
                self.send_html_file('templates/error.html', 404)

    def do_POST(self):
        data = self.rfile.read(int(self.headers['Content-Length']))
        print(data)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        client_socket.sendto(data, (SOCKET_HOST, SOCKET_PORT))
        client_socket.close()
        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self):
        pr_url = urllib.parse.urlparse(self.path)
        file_type = pr_url.path.split('.')[-1]
        file_base_path = "style" if file_type == 'css' else "public"
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        if mt:
            self.send_header("Content-type", mt[0])
        else:
            self.send_header("Content-type", 'text/plain')
        self.end_headers()
        with open(f'{file_base_path}{self.path}', 'rb') as file:
            self.wfile.write(file.read())

def save_data_from_form(data):
    data_parse = urllib.parse.unquote_plus(data.decode())
    data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
    try:
        with open('storage/data.json', 'w', encoding='utf-8') as fd:
            json.dump(data_dict, fd, ensure_ascii=False, indent=4)
    except ValueError as e:
        print(f'Error: {e}')
    except Exception as e:
        print(f'Error: {e}')

def run(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = (HTTP_HOST, HTTP_PORT)
    logging.debug(f'Start server on {HTTP_HOST}:{HTTP_PORT}')
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()
        logging.debug('Server stopped')


def run_socket_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server = SOCKET_HOST, SOCKET_PORT
    sock.bind(server)
    logging.debug(f'Start server on {SOCKET_HOST}:{SOCKET_PORT}')
    try:
         while True:
            data, address = sock.recvfrom(BUFFER_SIZE)
            logging.debug(f'Received data: {data.decode()} from: {address}')
            save_data_from_form(data)
    except KeyboardInterrupt:
        http.server_close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')
    server = threading.Thread(target=run, args=(HTTPServer, HttpHandler))
    socket_server = threading.Thread(target=run_socket_server)
    server.start()
    socket_server.start()
