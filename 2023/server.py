import http.server
import socketserver
import argparse

parser=argparse.ArgumentParser()
parser.add_argument('--port', type=int, default=8080)
args=parser.parse_args()


PORT = args.port
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()