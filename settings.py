#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# run sittings
# toaza.com
# amxku@sebug.net
#
#

import os.path

settings = {
    "xsrf_cookies": True,
    "cookie_secret": "JHLas,./+df&%#%^&jkjJKJg:KJO#I1@ET5$#asas212##@@#EQn#asd#2012",
    "static_path": os.path.join(os.path.dirname(__file__), "static"),
    "login_url": "/:signin",
    "autoescape": None,
    "gzip": True,
    #"debug": True,
    "debug": False,
}