#!/usr/bin/python
# (c) 2018 Jim Hawkins. MIT licensed, see https://opensource.org/licenses/MIT
# Part of Blender Driver, see https://github.com/sjjhsjjh/blender-driver
"""Blender Driver Application with various RESTful classes and interfaces.

This module is intended for use within Blender Driver and can only be used from
within Blender."""
# Exit if run other than as a module.
if __name__ == '__main__':
    print(__doc__)
    raise SystemExit(1)

# Standard library imports, in alphabetic order.
#
# Module for command line switches.
# https://docs.python.org/3/library/argparse.html
# The import isn't needed because this class uses the base class to get an
# object.
# import argparse
#
# HTTP server module
# https://docs.python.org/3/library/http.server.html
# Extra documentation:
# The handler rfile attribute uses the StreamReader API:
# https://docs.python.org/3/library/asyncio-stream.html?highlight=write#streamreader
# The handler wfile attribute uses the StreamWriter API:
# https://docs.python.org/3/library/asyncio-stream.html?highlight=write#streamwriter
from http.server import HTTPServer, SimpleHTTPRequestHandler
#
# Module for JavaScript Object Notation (JSON) strings.
# https://docs.python.org/3.5/library/json.html
import json
#
# Module for levelled logging messages.
# Tutorial is here: https://docs.python.org/3/howto/logging.html
# Reference is here: https://docs.python.org/3/library/logging.html
from logging import DEBUG, INFO, WARNING, ERROR, log
#
# Modules for path manipulation and changing the working directory.
# https://docs.python.org/3/library/os.html#os.chdir
# https://docs.python.org/3/library/os.path.html
from os import chdir
import os.path
#
# Module to create an HTTP server that spawns a thread for each request.
# https://docs.python.org/3/library/socketserver.html#module-socketserver
# The ThreadingMixIn is needed because of an apparent defect in Python, see:
# https://github.com/Microsoft/WSL/issues/1906
# https://bugs.python.org/issue31639
# The defect is fixed in 3.7 Python but Blender has the 3.5 version at time of
# writing.
from socketserver import ThreadingMixIn
#
# Module for starting a Thread.
# https://docs.python.org/3/library/threading.html
import threading
#
# Module for pretty printing exceptions.
# https://docs.python.org/3/library/traceback.html#traceback-examples
from traceback import print_exc
#
# Module for parsing URL strings.
# https://docs.python.org/3/library/urllib.parse.html
import urllib.parse
#
# Local imports.
#
# Application base class module.
from . import rest
#
# Path store utility.
from path_store.pathstore import pathify_split

class Application(rest.Application):
    
    @property
    def url(self):
        return self._url
    
    def _http_server(self):
        while not self.terminating():
            self._httpServer.handle_request()
    
    def game_initialise(self):
        super().game_initialise()
        website = self.arguments.directory
        if website is None:
            website = os.path.abspath(os.path.join(
                os.path.dirname(__file__), os.path.pardir, os.path.pardir
                , 'user_interface', 'diagnostic'))
        #
        # Change to the website directory so that the HTTP handler can be a
        # subclass of SimpleHTTPRequestHandler.
        chdir(website)
        #
        # Create the server object and open a port. Don't service any requests
        # here. That will happen on the http_server thread.
        self._httpServer = HTTPServer(
            ("localhost", self.arguments.port), Handler)
        #
        # Seems necessary to set a timeout in the HTTP server to avoid the
        # request thread hanging.
        self._httpServer.timeout = 0.5
        #
        # Set a reference to the application object into the server object for
        # later use by its request Handler.
        self._httpServer.application = self
        #
        # Get the actual port number and server address. The port number could
        # be different, if zero was specified.
        address = self._httpServer.server_address
        self._url = 'http://{}:{}'.format(
            'localhost' if address[0] == '127.0.0.1' else address[0]
            , int(address[1]))
        #
        # Start the server thread.
        log(INFO, 'Starting HTTP server at {}', self.url)
        threading.Thread(target=self._http_server, name="http_server").start()

    def game_terminate(self):
        log(INFO, 'Closing HTTP server ...')
        self._httpServer.server_close()
        log(INFO, 'HTTP server shut down.')
        super().game_terminate()

    def dont_join_reason(self, thread):
        if thread.name == 'http_server':
            return "HTTP server thread, which might be hung."
        return super().dont_join_reason(thread)

    # Override.
    def get_argument_parser(self):
        parser = super().get_argument_parser()
        parser.add_argument(
            '--port', type=int, default=0, help=
            'Port number on which to serve HTTP.'
            ' Default is to get the next available port.')
        parser.add_argument(
            '--directory', type=str, default=None, help=
            'Directory that contains the HTML for the user interface.'
            ' WARNING: The current working directory will change to that'
            ' directory. Default is to go up two levels from where this file'
            ' is located, then down into the user_interface/diagnostic/'
            ' sub-directory.')
        return parser
    
    def rest_api(self, httpHandler):
        url = urllib.parse.urlsplit(httpHandler.path)
        if url.path == '/api':
            path = list()
        elif url.path.startswith('/api/'):
            path = list(pathify_split(url.path, skip=1))
        else:
            path = None

        if path is None:
            return url
        
        with self.mainLock:
            generic = self._restInterface.get_generic(path)

            if generic is not None:
                response = bytes(json.dumps(generic), 'utf-8')
                httpHandler.send_response(200)
                httpHandler.send_header('Content-Type', 'application/json')
                httpHandler.send_header(
                    'Content-Length', '{}'.format(len(response)))
                httpHandler.end_headers()
                httpHandler.wfile.write(response)
                print('rest_api {} {} {}'.format(
                    url, path, json.dumps(generic, indent=2)))

        return None

# HTTP Server subclass. This class holds a reference to the Application object
# so that any handlers that are spawned have a route to it.
class HTTPServer(ThreadingMixIn, HTTPServer):
    @property
    def application(self):
        return self._application
    @application.setter
    def application(self, application):
        self._application = application
    
class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            url = self.server.application.rest_api(self)
        except:
            self.send_error(500)
            log(ERROR, 'Exception in Handler on thread"{}"'
                , threading.current_thread().name)
            raise
        if url is None:
            return
        return super().do_GET()
