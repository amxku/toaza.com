#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
#
#import formencode
from formencode import validators
import _db
#from blinker import signal
from ..helpers import temptime

class User(_db.thing.Thing):
    _tablename = 'users'
    _primary_key = 'uid'
    """
    username = formencode.All(
        validators.String(
            not_empty = True,
            strip = True,
            min = 4,
            max = 16,
            messages = {
                'empty': u'用户名不能为空',
                'tooLong': u'用户名不能大于 16 个字符',
                'tooShort': u'用户名不能少于 4 个字符',
            }),
        validators.PlainText(messages = {
            'invalid': u'用户名只能包含数字，字母，下划线'
        }))

    tagline = validators.String(
        strip = True,
        max = 64,
        messages={
            'tooLong':u'签名不能超过 64 个字符'
        })"""

    def user_new_sina(self,username,sinaid,flag):
        user_n = User()
        user_n.username = username
        user_n.sinaid = sinaid
        user_n.flag = flag
        user_n.regtime = temptime()
        user_n.save()
        return user_n.uid

    def user_new_google(self,username,email,flag):
        user_n = User()
        user_n.username = username
        user_n.email = email
        user_n.flag = flag
        user_n.regtime = temptime()
        user_n.isnofrist = 'F'
        user_n.save()
        return user_n.uid

    def update_avatar(self,uid):
        update_a = User().find_by_uid(uid)
        update_a.isavatar = temptime()
        update_a.save()

    def update_user_name(self,item,username,isnofrist,uid):
        update_n = User().find_by_uid_and_isnofrist(uid,isnofrist)
        update_n.item = item
        update_n.isnofrist = 'T'
        update_n.username= username
        update_n.save()

    def update_user(self,item,isnofrist,uid):
        update_n = User().find_by_uid_and_isnofrist(uid,isnofrist)
        update_n.item = item
        update_n.save()

    def update_user_flag(self,flag,uid):
        update_uf = User().find_by_uid(uid)
        update_uf.flag = flag
        update_uf.save()

    def update_only_username(self,username,uid):
        update_uf = User().find_by_uid(uid)
        update_uf.username = username
        update_uf.save()

class Article(_db.thing.Thing):
    _tablename = 'article'
    _primary_key = 'aid'

    title = validators.String(
        not_empty = True,
        strip = True,
        min = 4,
        max = 120,
        messages={
            'empty': u'标题不能为空',
            'tooLong':u'标题不能超过 120 个字符',
            'tooShort': u'标题不能少于 4 个字符',
        })

    def article_comcount(self,lctime,aid):
        comment_count = Article().find_by_aid(aid)
        comment_count.comtotal += 1
        comment_count.lastctime = lctime
        comment_count.save()

    def article_edit(self,title,content,aid):
        article_edit = Article().find_by_aid(aid)
        article_edit.title = title
        article_edit.content = content
        article_edit.save()

    def article_new(self,uid,title,content,aptime,lastctime):
        a_new = Article()
        a_new.uid = uid
        a_new.title = title
        a_new.content = content
        a_new.aptime = aptime
        a_new.lastctime = lastctime
        a_new.save()
        return a_new.aid

class Comment(_db.thing.Thing):
    _tablename = 'comments'
    _primary_key = 'cid'

    def comment_new(self,uid,aid,content,cptime):
        comments = Comment()
        comments.uid = uid
        comments.aid = aid
        comments.content = content
        comments.cptime = cptime
        comments.save()
        return comments.cid

class Node(_db.thing.Thing):
    _tablename = 'node'
    _primary_key = 'nid'

    def node_new(self,name,url):
        node_new = Node()
        node_new.nName = name
        node_new.nUrl = url
        node_new.save()
        return node_new.nid

    def node_admin_new(self,nName,nUrl,nDes,nType,subhead):
        admin_new_node = Node()
        admin_new_node.nName = nName
        admin_new_node.nUrl = nUrl
        admin_new_node.nDes = nDes
        admin_new_node.nType = nType
        admin_new_node.subhead = subhead
        admin_new_node.save()
        return admin_new_node.nid

    def node_admin_update(self,nName,nUrl,nDes,nType,subhead,nid):
        admin_node_edit = Node().find_by_nid(nid)
        admin_node_edit.nName = nName
        admin_node_edit.nUrl = nUrl
        admin_node_edit.nDes = nDes
        admin_node_edit.nType = nType
        admin_node_edit.subhead = subhead
        admin_node_edit.save()

    def node_count_update(self,counter,type,nid):
        admin_count = Node().find_by_nid_and_nType(nid,type)
        admin_count.nCou = counter
        admin_count.save()

class Log(_db.thing.Thing):
    _tablename = 'logs'
    _primary_key = 'lid'

    # 记录日志(type,des,aid,cid,nid,puid)
    def log_new(self,uid,optime,ipadds,optype,des,aid,cid,nid,puid):
        logs = Log()
        logs.uid = uid
        logs.optime = optime
        logs.ipadds = ipadds
        logs.optype = optype
        logs.des = des
        logs.aid = aid
        logs.cid = cid
        logs.nid = nid
        logs.puid = puid
        logs.save()
        return logs.lid

class Commentreid(_db.thing.Thing):
    _tablename = 'commentreid'
    _primary_key = 'crid'

    def commentr_new(self,uid,lid,atype):
        commentr = Commentreid()
        commentr.uid = uid
        commentr.lid = lid
        commentr.atype = atype
        commentr.save()

    def check_alerts_by_uid(self,crid):
        commentrid = Commentreid().find_by_crid(crid)
        commentrid.checked = '1'
        commentrid.save()

class Noderelated(_db.thing.Thing):
    _tablename = 'noderelated'
    _primary_key = 'nrid'

    def noderelated_new(self,aid,nid):
        node_rid_new = Noderelated()
        node_rid_new.aid = aid
        node_rid_new.nid = nid
        node_rid_new.save()
