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
# https://docs.python.org/3/library/http.server.html#module-http.server
# https://docs.python.org/3/library/socketserver.html#module-socketserver
import http.server
#
# The ThreadingMixIn is needed because of a defect in Python, see these:
# https://github.com/Microsoft/WSL/issues/1906
# https://bugs.python.org/issue31639
# The defect is fixed in 3.7 Python but Blender has the 3.5 version at time of
# writing.
from socketserver import ThreadingMixIn
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
# Module for starting a Thread.
# https://docs.python.org/3/library/threading.html
import threading
#
# Module for parsing URL strings.
# https://docs.python.org/3/library/urllib.parse.html
import urllib.parse
#
# Local imports.
#
# Application base class module.
from . import rest

class Application(rest.Application):
    
    @property
    def httpPort(self):
        return self._httpPort
    
    def _http_server(self):
        print('_http_server 0')
        self.continueServing = True
        while self.continueServing and not self.terminating():
            print('_http_server 1', self._httpServer.timeout)
            self._httpServer.handle_request()
                
    #     try:
    #         self._httpServer.serve_forever()
    #     except:
    #         print('_http_server exception')
        print('_http_server 2', self.continueServing)
    
    @property
    def continueServing(self):        
        return self._continueServing
    @continueServing.setter
    def continueServing(self, continueServing):
        self._continueServing = continueServing
    
    def game_initialise(self):
        super().game_initialise()
        print(self.pythonVersion)
        website = self.arguments.directory
        if website is None:
            website = os.path.abspath(os.path.join(
                os.path.dirname(__file__), os.path.pardir, os.path.pardir
                , 'user_interface'))
        #
        # Change to the website directory so that the HTTP handler can be a
        # subclass of SimpleHTTPRequestHandler.
        chdir(website)
        #
        # Create the server object and open a port. Don't service any requests
        # here. That will happen on the http_server thread.
        self._httpServer = HTTPServer(
            ("localhost", self.arguments.port), Handler)
        self._httpServer.timeout = 0.5
        #
        # Set a reference to the owner object into the server object for later
        # use by its request Handler.
        self._httpServer.application = self
        #
        # Get the actual port number and server address.
        sockname = self._httpServer.server_address
        self._httpServerAddress = (
            'localhost' if sockname[0] == '127.0.0.1' else sockname[0])
        self._httpPort = int(sockname[1])
        log(INFO, 'Started HTTP server on {}:{}.'
            , self._httpServerAddress, self._httpPort)
        #
        # Create the http_server thread object but don't start the thread yet.
        self._httpServerThread = threading.Thread(
            target=self._http_server, name="http_server")
        
        log(INFO, 'Starting HTTP server ...')
        self._httpServerThread.start()

    def game_terminate(self):
        super().game_terminate()

        # log(INFO, 'Stop HTTP service ...')
        # self._httpServer.shutdown()
        log(INFO, 'Closing HTTP server ...')
        self._httpServer.server_close()
        #
        # It seems necessary to do both of the above before the following. If
        # the thread join is before the server_close, it hangs if any error has
        # been returned.
        # log(INFO, 'Joining HTTP server thread ...')
        # self._httpServerThread.join()
        log(INFO, 'HTTP server shut down.')
        # super().game_terminate()

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
            ' is located, then down into the user_interface/ sub-directory.')
        return parser
    
    def rest_api(self, handler):
        url = urllib.parse.urlsplit(handler.path)
        api = url.path.startswith('/api/') or url.path == '/api'
        if (not api) and handler.command == 'GET':
            return False

        print('rest_api(,{},{})'.format(handler, url))
        handler.send_error(501)
        return True

# HTTP Server subclass. This class holds a reference to the Application object
# so that any handlers that are spawned have a route to it.
class HTTPServer(ThreadingMixIn, http.server.HTTPServer):
    @property
    def application(self):
        return self._application
    @application.setter
    def application(self, application):
        self._application = application
        
    # # Override
    # def handle_error(self, request, clientAddress):
    #     # super().handle_error(request, clientAddress)
    #     print('Custom handle_error raise.')
    #     raise

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        try:
            handled = self.server.application.rest_api(self)
        except:
            self.send_error(500)
            # self.server.application.continueServing = False
            raise
        if not handled:
            super().do_GET()
 