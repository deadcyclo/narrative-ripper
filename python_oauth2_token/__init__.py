import requests
import SimpleHTTPServer
import SocketServer
import subprocess
import webbrowser
import sys
import threading
from base64 import b64encode

HOST = 'http://localhost'
PORT = 4576

def _parse_query(string):
    try: return {d[0]: d[1] for d in [
            p.split('=') for p in string.split('?')[1].split('&')]}
    except: return {}

def get_token(client_id, client_secret, callback, host=HOST, port=PORT):
    redirect_uri='{host}:{port}'.format(host=host, port=port)
    server = None
    event = threading.Event()

    class OauthHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

        def do_GET(self):
            query = _parse_query(self.path)

            if query and 'code' in query:
                resp = requests.post('https://narrativeapp.com/oauth2/token/',
                    params={
                        'grant_type': 'authorization_code',
                        'code': query['code'],
                        'redirect_uri': redirect_uri,
                        'client_id': client_id
                    },
                    headers={
                        'Authorization': "Basic {}".format(
                            b64encode("{}:{}".format(client_id, client_secret)))
                    })

                callback(resp.json())
                event.set()
            return SimpleHTTPServer.SimpleHTTPRequestHandler.do_GET(self)

    class OauthThread(threading.Thread):
        def run(self):
            while not event.is_set():
                if not hasattr(self, 'server'):
                    self.server = SocketServer.TCPServer(('', port), OauthHandler)
                    thread = threading.Thread(target=self.server.serve_forever)
                    thread.deamon = True
                    thread.start()
            self.server.shutdown()

    thread = OauthThread()
    thread.deamon = True
    thread.start()

    url = "https://narrativeapp.com/oauth2/authorize/?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}".format(
            client_id=client_id, redirect_uri=redirect_uri)

    if sys.platform == 'darwin':  # OS X
        subprocess.Popen(['open', url])
    else:
        webbrowser.open_new_tab(url)
