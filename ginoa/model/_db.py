#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# db c
# toaza.com
#
import ginoa.extensions.thing as thing

db_config = {
    'master' :{
        'url':'mysql://ginoa:ginoa@127.0.0.1:3306/ginoa?charset=utf8',
        'echo':False, #True,False
        'pool_recycle':3600, #1小时链接一次
        'pool_size':100, #连接数大小
        'max_overflow':10, #超出pool_size后可允许的最大连接数
        },
    'slave' :{
        'url':'mysql://ginoa:ginoa@127.0.0.1:3306/ginoa?charset=utf8',
        'echo':False,
        'pool_recycle':3600,
        'pool_size':100, 
        'max_overflow':10,
        },
    }

thing.Thing.db_config(db_config)