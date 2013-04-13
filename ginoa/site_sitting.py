#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# site sittings
# toaza.com
#
##session 过期时间, days
PERMANENT_SESSION_LIFETIME = 1

#站点设置
##site name
SITE_NAME = 'Toaza'
SITE_VERSION = '0.1.3 - dev'
#程序本版
SITE_URL = 'http://toaza.com'

##login control
CHECK_LOGIN = 1
#控制老用户登录，0禁止
CHECK_REG = 1
#控制新用户登录，0禁止

#登录配置
SINA_CONSUMER_SECRET = 'aaa'
SINA_CONSUMER_KEY = 'aaaaa'
SINA_redirect_uri = 'http://toaza.com/:signin:sinacallback'

QQ_CONSUMER_SECRET = ''
QQ_CONSUMER_KEY = ''

##
pnum = 20
# 分页，每页数量
adminpnum = 15
# 管理分页
node_total = 120
#node数量
comm_total = 100
#评论显示数量
NOTIFY_MEMBER_NUM = 10
#一个帖子或回复可允许最多 @username 的人数


##图片存储方式，upyun
DOMAIN_NAME_AVATAR = 'aaaa'
#存放头像
AVATAR_LARGE = '!72.png'
#72px 缩略图
AVATAR_NORMAL = '!48.png'
#48px 缩略图
AVATAR_MINI = '!24.png'
#24px 缩略图

UPYUN_USER = 'aaa'
#操作用户
UPYUN_PW = 'aaa'
#操作用户密码

#头像图片网址前缀
AVATAR_URL = '/static/img'
#图片
STATIC_URL = '/static/file'
#文件(JS、CSS)
