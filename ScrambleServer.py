import http.server
import requests
import os
import uuid
from urllib.parse import unquote, parse_qs
import threading
from socketserver import ThreadingMixIn
from DatabaseInterface import DatabaseConnector

remote_url = 'https://url-scrambler.herokuapp.com/'

db = DatabaseConnector(remote=False)

f = open("index.html", "r")
form = f.read()


def CheckURI(uri, timeout=5):
    '''Check whether this URI is reachable, i.e. does it return a 200 OK?

    This function returns True if a GET request to uri returns a 200 OK, and
    False if that GET request returns any other response, or doesn't return
    (i.e. times out).
    '''
    try:
        r = requests.get(uri, timeout=timeout)
        # If the GET request returns, was it a 200 OK?
        return r.status_code == 200
    except requests.RequestException:
        # If the GET request raised an exception, it's not OK.
        return False


class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # A GET request will either be for / (the root path) or for /some-name.
        # Strip off the / and we have either empty string or a name.
        name = unquote(self.path[1:])

        if name:
            if name == 'Utility.js':
                self.send_response(200)
                self.send_header('Content-type', 'text/css')
                self.end_headers()
                javascript = open('Utility.js')
                javascript = javascript.read()
                self.wfile.write(javascript.encode())
            elif db.select(name) != None:
                # We know that name! Send a redirect to it.
                self.send_response(303)
                self.send_header('Location', db.select(name))
                self.end_headers()
            else:
                # We don't know that name! Send a 404 error.
                self.send_error(404, 'URI specification "{}" not found'.format(name))
        else:
            # Root path. Send the form.
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            # List the known associations in the form.
            #known = "\n".join("{} : {}".format(key, memory[key])
            #                  for key in sorted(memory.keys()))
            self.wfile.write(form.encode())

    def do_POST(self):
        # Decode the form data.
        length = int(self.headers.get('Content-length', 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)
        try:
            longuri = params["longuri"][0]
        except:
            longuri = ""
        shortname = str(uuid.uuid1())   # generate uid

        ip = self.client_address[0]     # ip address of client doing request

        if CheckURI(longuri) and longuri:
            db.insert(longuri, shortname, ip)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            #url = str(self.server.server_name) + ':' + str(self.server.server_port) + '/' + shortname
            url = remote_url + shortname
            htmlStuff = '<div><label>Scrambled URL for "{}":</label>' \
                        '<input type="url" class="form-control" value="{}" id="myInput">' \
                        '<button onclick="copyField()" class="btn btn-info">Copy URL</button></div>'.format(longuri, url)
            self.wfile.write(htmlStuff.encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("<div>Couldn't fetch URL '{}'</div>".format(longuri).encode())


class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."


if __name__ == '__main__':
    server_address = ('', int(os.environ.get('PORT', '8000')))
    httpd = ThreadHTTPServer(server_address, Shortener)
    httpd.serve_forever()
