#!/usr/bin/env python2
# encoding: utf-8
"""
JSON Server

Get a fake REST API with zero coding in seconds.

Inspired by https://github.com/typicode/json-server

THIS IS A WORK IN PROGRESS.

"""

# Model for this program:
# - http://stackoverflow.com/questions/23475615/how-do-i-send-and-receive-http-post-requests-in-python

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import json

HTTP_STATUS_OK = 200
HTTP_STATUS_NOTFOUND = 404
HTTP_STATUS_BADREQUEST = 400

ADDR = "localhost"
PORT = 5000


class RequestHandler(BaseHTTPRequestHandler):
    """Return json data from URL.

    URLs must be 3 or 4 levels deep.

    Examples:
    - /careers/1/people
    - /careers/1/people/add
    - /people
    - /people/add
    - /careers/1/edit

    URLs are composed by object, id, dependant and verb:

     /careers/146/people/add
        |      |    |     |
        |      |    |     +---> verb
        |      |    +---------> dependant
        |      +--------------> id
        +---------------------> object

    Verbs must be:
    - add
    - edit
    - delete

    """

    def do_GET(self):
        print(self.path)
        parts = [s for s in self.path.split("/") if s]

        # -----------------------------------------------------
        # Test malformed URLs.
        # -----------------------------------------------------

        if not parts:
            self._print("Type some parameter in URL",
                        status=HTTP_STATUS_BADREQUEST)
            return
        if len(parts) > 4:
            # Force API maximum level limit.
            # Example: /people/1/children/add
            self._print("Too many parameters in URL",
                        status=HTTP_STATUS_BADREQUEST)
            return

        # -----------------------------------------------------
        # If last part is a verb (`add` or `edit`), it's the
        # first step in a 2-way procedure.
        #
        # 1st step: show a form to add or edit the object.
        # 2nd step: will be sent via POST method.
        #
        # The `delete` verb is sent via POST. If there's some
        # confirmation screen, it's showed by a normal GET
        # request on the object.
        # -----------------------------------------------------

        if parts[-1] in "add edit".split():
            # A verb to show form for an action.
            # Examples:
            # - /people/add
            # - /people/1/edit
            self._print("")
            return

        # -----------------------------------------------------
        # Let's work.
        # -----------------------------------------------------

        object_ = id_ = dependant = None

        try:
            object_ = parts[0]
            id_ = parts[1]
            dependant = parts[2]
        except IndexError:
            pass

        if object_:
            # Example URL: /people
            data = [x for x in JSONDATA[object_]]

        if id_:
            # Example URL: /people/1
            data = [x for x in data if x["id"] == int(id_)]
            try:
                data = data[0]
            except IndexError:
                data = None

        if dependant:
            # Example URL: /careers/1/people
            k = object_ + "_id"
            data = [x for x in JSONDATA.get(dependant, [])
                    if x.get(k, 0) == int(id_)]

        if not data:
            self._print("Not Found", status=HTTP_STATUS_NOTFOUND)
            return

        data_s = json.dumps(data, indent=4)
        self._print(data_s)

    def _print(self, message, status=None):
        status = status or HTTP_STATUS_OK
        self.send_response(status, "OK")
        self.end_headers()
        self.wfile.write(message)


if __name__ == "__main__":
    with open("db.json") as f:
        JSONDATA = json.loads(f.read())

    httpd = HTTPServer((ADDR, PORT), RequestHandler)
    httpd.serve_forever()
