#!/usr/bin/env python
# -*- coding:utf-8 -*-
# run site
#
# toaza.com
# amxku@sebug.net（2012/9）
#
#
import sys,os

import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.options import options
from urls import urls
from settings import settings

os.environ['PYTHON_EGG_CACHE'] = '/tmp/python-eggs'

try:
    port = int(sys.argv[1].split('=')[1])
except:
    port = '1818'

def main():
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(tornado.web.Application(urls,**settings), xheaders=True)
    #http_server.listen(port,'0.0.0.0')
    http_server.listen(port,'127.0.0.1')
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

