#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# url setting
# toaza.com
#
import ginoa.x_views
import ginoa.x_account
import ginoa.zz_main

urls = [
    (r"/", ginoa.x_views.main_index),
    (r"/newpost", ginoa.x_views.newpost),
    (r"/post:del", ginoa.x_views.delpost),
    (r"/a/(\d+)", ginoa.x_views.ashow),
    (r"/newcomment", ginoa.x_views.newcomment),
    (r"/n/([^/]+)", ginoa.x_views.nlists),
    (r"/recent", ginoa.x_views.listrecent),
    #
    (r"/signout", ginoa.x_account.signout),
    (r"/:signin", ginoa.x_account.signin),
    (r"/:signin:sina", ginoa.x_account.signin_sina),
    (r"/:signin:sinacallback", ginoa.x_account.sina_callbackpage),
    (r"/:signin:google", ginoa.x_account.signin_google),

    (r"/settings", ginoa.x_account.authset),
    (r"/user:alerts", ginoa.x_account.alerts),
    (r"/user:alerts:del", ginoa.x_account.alertsdel),
    (r"/settings:avatar", ginoa.x_account.avatarupload),
    (r"/u/([^/]+)", ginoa.x_account.view_user),

    # admin
    (r"/zzginoa/", ginoa.zz_main.zz_index),
    (r"/zzginoa/articles", ginoa.zz_main.zz_articles),
    (r"/zzginoa/nodes", ginoa.zz_main.zz_nodes),
    (r"/zzginoa/users", ginoa.zz_main.zz_users),
    (r"/zzginoa/comments", ginoa.zz_main.zz_comments),
    (r"/zzginoa/comments:del", ginoa.zz_main.zz_comments_del),
    (r"/zzginoa/logs", ginoa.zz_main.zz_logs)
]
