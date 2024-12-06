from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import bot
import os

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot is running')

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    # Start bot in a separate thread
    bot_thread = threading.Thread(target=bot.main)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Run HTTP server in main thread
    run_server()
