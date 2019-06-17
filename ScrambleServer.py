import http.server
import requests
import os
import uuid
import json
from http import cookies
from urllib.parse import unquote, parse_qs
import threading
from socketserver import ThreadingMixIn
from DatabaseInterface import DatabaseConnector

remote_url = 'https://url-scrambler.herokuapp.com/'

db = DatabaseConnector(remote=True)

f = open("index.html", "r")
form = f.read()


def CheckURI(uri, timeout=5):
    '''Check whether this URI is reachable, i.e. does it return a 200 OK?
    If there are any other responses or it times out, it's not reachable.
    '''
    try:
        request_headers = {
            'user-agent': 'url-scrambler'   # need custom user-agent or sites may send a 429 (too many requests)
        }
        r = requests.get(uri, timeout=timeout, headers=request_headers)
        # If the GET request returns, was it a 200 OK?
        return r.status_code == 200
    except requests.RequestException:
        # If the GET request raised an exception, it's not OK.
        return False


def ConvertURI(uri):
    uri_dot = uri.split('.')
    uri_slash = uri.split('/')

    if uri_dot[0] == 'www':
        return 'http://' + uri  # user gave domain level url with www, such as 'www.google.ca'
    elif uri_dot[0] != 'http://www' and uri_dot[0] != 'https://www'\
            and uri_slash[0] != 'http:' and uri_slash[0] != 'https:':
        return 'http://www.' + uri  # user gave domain level url 'google.ca'
    else:
        return uri  # user gave complete url, either 'https://google.ca' or 'https://www.google.ca'


class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # A GET request will either be for / (the root path) or for /some-name.
        # Strip off the / and we have either empty string or a name.
        name = unquote(self.path[1:])

        if 'cookie' not in self.headers:
            cookieId = uuid.uuid1()
            c = cookies.SimpleCookie()
            c['yourId'] = cookieId
            c['yourId']['max-age'] = 60 * 60 * 24 * 365   # 1 year for cookie
            print(c['yourId'].value)

            self.send_response(303)  # redirect via GET
            self.send_header('Location', '/')
            self.send_header('Set-Cookie', c['yourId'].OutputString())
            self.end_headers()
            return  # don't need to run the rest of code if this is the first visit

        if name:
            if name == 'Utility.js':
                self.send_response(200)
                self.send_header('Content-type', 'application/javascript')
                self.end_headers()
                javascript = open('Utility.js')
                javascript = javascript.read()
                self.wfile.write(javascript.encode())
            elif name == 'PastUrls':
                c = cookies.SimpleCookie(self.headers['cookie'])
                cookieId = c['yourId'].value
                pastUrls = dict(db.selectIdUrls(cookieId))  # convert list of tuples to dictionary
                for key in pastUrls:
                    pastUrls[key] = remote_url + pastUrls[key]  # add remote_url to complete the URL link
                pastUrls = json.dumps(pastUrls)

                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write((str(pastUrls).encode()))
            elif db.select(name) is not None:
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
            self.wfile.write(form.encode())

    def do_POST(self):
        # Decode the form data.
        length = int(self.headers.get('Content-length', 0))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)
        try:
            longuri = params["longuri"][0]
            longuri_converted = ConvertURI(longuri)
        except:
            longuri = ""
            longuri_converted = ""
        shortname = str(uuid.uuid1())   # generate uid

        ip = self.client_address[0]     # ip address of client doing request
        c = cookies.SimpleCookie(self.headers['cookie'])
        cookieId = c['yourId'].value

        if CheckURI(longuri_converted) and longuri:
            db.insert(longuri_converted, shortname, ip, cookieId)

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            #url = str(self.server.server_name) + ':' + str(self.server.server_port) + '/' + shortname
            url = remote_url + shortname

            response = {
                "longurl": longuri,
                "shorturl": url
            }
            jsonStuff = json.dumps(response)
            self.wfile.write(jsonStuff.encode())
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write("Couldn't fetch URL '{}'".format(longuri).encode())


class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."


if __name__ == '__main__':
    try:
        server_address = ('', int(os.environ.get('PORT', '8000')))
        httpd = ThreadHTTPServer(server_address, Shortener)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Interrupted from command line. Closing server.')
        httpd.shutdown()
