from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import bot
import os
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        status = f'Bot is running\nLast check: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        self.wfile.write(status.encode())
        logging.info(f"Health check request from {self.client_address[0]}")

def run_server():
    port = int(os.environ.get('PORT', 10000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    logging.info(f'Starting server on port {port}...')
    httpd.serve_forever()

if __name__ == '__main__':
    # Start bot in a separate thread
    logging.info('Starting bot thread...')
    bot_thread = threading.Thread(target=bot.main)
    bot_thread.daemon = True
    bot_thread.start()
    logging.info('Bot thread started')
    
    # Run HTTP server in main thread
    run_server()
