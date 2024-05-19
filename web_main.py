#!/usr/bin/python
import argparse
import copy
import json
import os
import sys
import urllib

import requests
import uuid
from time import sleep

from urllib.parse import urlparse

from http.server import BaseHTTPRequestHandler, HTTPServer
from os import curdir, sep
from openai_wrapper import OpenAIWrapper
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pattern_search import PatternSearch

PORT_NUMBER = 8080
MAX_VALID_PERIOD_FOR_JWT = 60


# This class will handles any incoming request from
# the browser
class Server(BaseHTTPRequestHandler):
    messagesReceived = ["waiting"]
    mfa_admin_token = ""
    conf = None
    api_instance = None
    init_responses = {}
    openai_wrapper = None

    def __int__(self):
        args = None

        init_responses = {}

    '''Poll for status of a previous verify request'''

    def do_POST(self):
        self.send_response(200)
        self.send_header('Content-type', "application/json")
        self.end_headers()

    def do_find_key_words(self, sentence):
        patternSearch = PatternSearch()
        answer = patternSearch.search_occurrences_of_keywords(self.openai_wrapper, sentence, self.conf["file_path"])
        return answer

    def do_ask_and_pattern_search(self, question):
        answer = self.openai_wrapper.ask(question)
        reply = {"ai_answer": answer}
        reply.update({"pattern_results": self.do_find_key_words(question)})
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        json_object = json.dumps(reply)
        self.wfile.write(json_object.encode())

    def do_ask(self, question):
        answer = self.openai_wrapper.ask(question)
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        reply = {"ai_answer": answer}
        json_object = json.dumps(reply)
        self.wfile.write(json_object.encode())

    def send_html(self, path):
        mimetype = 'text/html'
        f = open(curdir + sep + path, 'rb')
        self.send_response(200)
        self.send_header('Content-type', mimetype)
        self.end_headers()
        self.wfile.write(f.read())
        f.close()

    # Handler for the GET requests
    def do_GET(self):
        if (self.path.endswith('?')):
            self.path = "/" + self.path.rstrip('?')
        if self.path == "/":
            self.path = "/index.html"
        if "ask_and_split" in self.path:
            print("in ask")
            query = urlparse(self.path).query
            query_components = dict(qc.split("=") for qc in query.split("&"))
            question = query_components["question"]
            question = urllib.parse.unquote(question, encoding='utf-8', errors='replace')
            print(question)
            self.do_ask_and_pattern_search(question)
        # if "ask" in self.path:
        #     print("in ask")
        #     query = urlparse(self.path).query
        #     query_components = dict(qc.split("=") for qc in query.split("&"))
        #     question = query_components["question"]
        #     question = urllib.parse.unquote(question, encoding='utf-8', errors='replace')
        #     print(question)
        #     self.do_ask(question)

        try:
            # Check the file extension required and
            # set the right mime type

            sendReply = False
            if self.path.endswith(".html"):
                mimetype = 'text/html'
                sendReply = True
            if self.path.endswith(".jpg"):
                mimetype = 'image/jpg'
                sendReply = True
            if self.path.endswith(".gif"):
                mimetype = 'image/gif'
                sendReply = True
            if self.path.endswith(".png"):
                mimetype = 'image/png'
                sendReply = True
            if self.path.endswith(".js"):
                mimetype = 'application/javascript'
                sendReply = True
            if self.path.endswith(".css"):
                mimetype = 'text/css'
                sendReply = True

            if sendReply == True:
                f = open(curdir + sep + self.path, 'rb')
                self.send_response(200)
                self.send_header('Content-type', mimetype)
                self.end_headers()
                self.wfile.write(f.read())
                f.close()
            return
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def get_a_user(self, email):
        pass


# method to start HTTP server
def http_server(responseReceived, api_instance, configuration):
    try:
        Server.messagesReceived = responseReceived
        Server.conf = configuration
        Server.api_instance = api_instance
        with open("initial.conf") as conf_file:
            configuration = json.load(conf_file)
        wannabe_masterdoc = []
        text_splitter = RecursiveCharacterTextSplitter()
        for subdir, dirs, files in os.walk(configuration["file_path"]):
            for file in files:
                with open(configuration["file_path"] + "\\" + file) as idplus_file:
                    wannabe_masterdoc += (text_splitter.create_documents(idplus_file.readlines()))

        Server.openai_wrapper = OpenAIWrapper(org_id=configuration["openai_conf"]["org_id"],
                                              api_key=configuration["openai_conf"]["api_key"])
        Server.openai_wrapper.process_documents(wannabe_masterdoc)
        server = HTTPServer(('', PORT_NUMBER), Server)
        print('Started httpserver on port ', PORT_NUMBER)

        # Wait forever for incoming htto requests
        server.serve_forever()

    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        server.socket.close()


CONF_FILE_OPTION = "-f"
CONF_FILE_OPTION_LONG = "--confFile"
CONF_FILE_DESCRIPTION = "Required parameters such as file path ro search for, open_ai key etc"


def parse_args(args):
    parser = argparse.ArgumentParser(description="Sample")
    parser.add_argument(CONF_FILE_OPTION, CONF_FILE_OPTION_LONG, required=True,
                        help=CONF_FILE_DESCRIPTION)

    parsed_args = parser.parse_args(args)
    return parsed_args


if __name__ == '__main__':
    import threading

    #
    # #
    args = parse_args(sys.argv[1:])
    # token = generate_token(args)
    # print(token)
    api_instance = {}

    with open(args.confFile) as conf_file:
        configuration = json.load(conf_file)
    #
    responseReceived = []
    from multiprocessing import Process

    p = Process(target=http_server, args=(responseReceived, api_instance, configuration))
    p.start()
    p.join()
