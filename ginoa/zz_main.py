#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# admin
# toaza.com
#
import tornado.web
from tornado.escape import xhtml_escape
from base import RequestHandler
from site_sitting import *
from helpers import clear2nbsp, pickle_loads, checkuserflag
from model.testm import User, Article, Comment, Node, Noderelated, Log, Commentreid
# db model (sqlalchemy)


class zz_index(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        if self.session['gnaflag'] != '675':
            raise tornado.web.HTTPError(404)
            return

        try:
            op = xhtml_escape(self.get_argument('op', 'index'))
            next = xhtml_escape(self.get_argument('next', './'))
        except:
            self.get_error('/', '10', u'error', 'toaza.com')
            return

        if op == 'index':
            results_user_counter = User().count()
            results_article_counter = Article().count()
            results_comments_counter = Comment().count()
            results_nodes_counter = Node().count()
            results_logs_counter = Log().count()

            countent = self.render_template('zz_main.html',
                nodes_Count = results_nodes_counter,
                user_Count = results_user_counter,
                article_Count = results_article_counter,
                comments_Count = results_comments_counter,
                logs_Count = results_logs_counter,
                title = u'Management',)
            self.write(countent)
        elif op == 'flush_node_total':
            nodes = Node().findall_by_nType('N',limit=Node().where('nType','=','N').count())
            for n in nodes:
                Node().node_count_update(Noderelated().count_by_nid(n.nid),'N',n.nid)
            self.get_error(next, '4', u'节点刷新完成', 'toaza.com')
            return
        elif op == 'flush_class_total':
            classs = Node().findall_by_nType('C',limit=Node().where('nType','=','C').count())
            for c in classs:
                Node().node_count_update(Node().where('nType','=','N').count_by_subhead(c.nid),'C',c.nid)
            self.get_error(next,'4',u'分类刷新完成','toaza.com')
            return
        else:
            self.get_error('/zzginoa/','10',u'参数错误','toaza.com')
            return

class zz_articles(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        if self.session['gnaflag'] <> '675':
            raise tornado.web.HTTPError(404)
            return
        pageid = int(self.get_argument("p",1))
        aTotal = Article().count()
        if aTotal:
            if aTotal % adminpnum == 0:
                pages = aTotal / adminpnum
            else:
                pages = aTotal / adminpnum + 1
            offset = (pageid-1) * adminpnum
            articles = []
            aarticles = Article().select(['uid','aid','title','aptime','comtotal']).order_by('-lastctime').findall(adminpnum,offset)
            for iai in aarticles:
                auser = User().select(['username']).find_by_uid(iai.uid).to_dict()
                iai = iai.to_dict()
                arts = auser.copy()
                arts.update(iai)
                articles.append(arts)

        countent = self.render_template('zz_articles.html',
            articles = articles,
            aTotal = aTotal,
            f1page = '/zzginoa/articles',
            f1pagewa = '?',
            thisp = pageid,
            Totalp = pages,
            title = u'主题管理 %s/%s' % (pageid,pages),)
        self.write(countent)

class zz_comments(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        if self.session['gnaflag'] <> '675':
            raise tornado.web.HTTPError(404)
            return
        access_token = str(self.get_cookie('_part',''))
        pageid = int(self.get_argument("p",1))
        aTotal = Comment().count()
        if aTotal:
            if aTotal % adminpnum == 0:
                pages = aTotal / adminpnum
            else:
                pages = aTotal / adminpnum + 1
            offset = (pageid-1) * adminpnum

            comments = []
            comms = Comment().order_by('-cptime').findall(adminpnum,offset)
            for ci in comms:
                aidtitle = Article().select(['title']).find_by_aid(ci.aid).to_dict()
                uidname = User().select(['username']).find_by_uid(ci.uid).to_dict()
                arts = ci.to_dict().copy()
                arts.update(aidtitle)
                arts.update(uidname)
                comments.append(arts)

        countent = self.render_template('zz_comments.html',
            comments = comments,
            aTotal = aTotal,
            f1page = '/zzginoa/comments',
            f1pagewa = '?',
            thisp = pageid,
            Totalp = pages,
            access_token = access_token,
            title = u'评论管理',)
        self.write(countent)

class zz_comments_del(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        if self.session['gnaflag'] <> '675':
            raise tornado.web.HTTPError(404)
            return

        token = self.get_argument('token', '0')
        access_token = str(self.get_cookie('_part',''))
        if token != access_token:
            self.get_error('/','10',u'参数异常',SITE_NAME)
            return

        cid = int(self.get_argument("id",0))
        del_cid = Comment().select(['cid']).find_by_cid(cid)
        del_lid = Log().select(['lid']).find_by_cid(del_cid.cid)
        self.logaw('admin',u'删除评论','0',cid,'0','0') #记录日志(type,des,aid,cid,nid,puid)
        try:
            Commentreid().where('lid','=',del_lid.lid).find().delete()
        except:
            pass
        try:
            Log().find_by_cid(del_cid.cid).delete()
        except:
            pass
        try:
            Comment().find_by_cid(cid).delete()
        except:
            pass

        self.get_error('javascript:history.go(-1);','10',u'删除成功','toaza.com')
        return

class zz_nodes(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        if self.session['gnaflag'] <> '675':
            raise tornado.web.HTTPError(404)
            return

        try:
            op = xhtml_escape(self.get_argument('op','index'))
            pageid = int(self.get_argument("p",1))
            nid = int(self.get_argument("nid",0))
            nType = xhtml_escape(self.get_argument('nType','N'))
        except:
            self.get_error('/zzginoa/nodes','10',u'error','toaza.com')
            return

        if nType == 'C':
            subheadsql = '1'
        else:
            subheadsql = '0'

        if op == 'index':
            nTotal = Node().where('subhead','!=',subheadsql).count_by_nType(nType)
            if nTotal:
                if nTotal % adminpnum == 0:
                    pages = nTotal / adminpnum
                else:
                    pages = nTotal / adminpnum + 1
                offset = (pageid-1) * adminpnum
                nodess = Node().where('subhead','!=',subheadsql).order_by('-nCou').findall_by_nType(nType,limit=adminpnum,offset=offset)
                nodeCids = Node().select(['nid','nName']).findall_by_nType('C')

                countent = self.render_template('zz_nodes.html',
                    nodes = nodess,
                    classs = nodeCids,
                    f1page = '/zzginoa/nodes' + str('?op='+op+'&amp;nType='+nType),
                    f1pagewa = '&',
                    thisp = pageid,
                    Totalp = pages,
                    nType = nType,
                    nTotal = nTotal,
                    op = op,
                    title = u'节点管理',)
                self.write(countent)
            else:
                self.get_error('/','10',u'None','toaza.com')
                return
        elif op == 'nosub':
            #未分类
            nTotal = Node().where('subhead','=','0').count_by_nType('N')
            if nTotal:
                if nTotal % adminpnum == 0:
                    pages = nTotal / adminpnum
                else:
                    pages = nTotal / adminpnum + 1
                offset = (pageid-1) * adminpnum

                nodes = []
                nids = Node().where('subhead','=','0').findall_by_nType('N',limit=adminpnum,offset=offset)
                for ns in nids:
                    if ns.subhead:
                        sub = Node().select(['nName']).find_by_nid(ns.subhead)
                        ns.subhead = sub
                    nodes.append(ns.to_dict())

                countent = self.render_template('zz_nodes.html',
                    nodes = nodes,
                    f1page = '/zzginoa/nodes' + str('?op='+op+'&amp;nType='+nType),
                    f1pagewa = '&',
                    thisp = pageid,
                    Totalp = pages,
                    nType = nType,
                    nTotal = nTotal,
                    op = op,
                    title = u'节点管理',)
                self.write(countent)
            else:
                self.get_error('/zzginoa/nodes','2',u'None','toaza.com')
                return
        elif op == 'edit':
            node = Node().find_by_nid(nid)
            classs = Node().findall_by_nType('C')
            countent = self.render_template('zz_nodes_edit.html',
                node = node,
                classs = classs,
                title = u'编辑 - 节点管理',)
            self.write(countent)
        elif op == 'add':
            classs = Node().findall_by_nType('C')
            node = None
            countent = self.render_template('zz_nodes_edit.html',
                node = node,
                classs = classs,
                title = u'添加 - 节点管理',)
            self.write(countent)
        else:
            self.get_error('/zzginoa/nodes','10',u'参数错误','toaza.com')
            return

    @tornado.web.authenticated
    def post(self):
        if self.session['gnaflag'] <> '675':
            raise tornado.web.HTTPError(404)
            return

        node_nName = unicode(xhtml_escape(self.get_argument('nName', '').strip()))
        node_nUrl = clear2nbsp(xhtml_escape(self.get_argument('nUrl', '').strip().lower()))
        node_nDes = unicode(xhtml_escape(self.get_argument('nDes', '').strip()))
        node_nType = xhtml_escape(self.get_argument('nType', 'N'))
        node_subhead = int(self.get_argument('subhead', '0'))
        nid = int(self.get_argument('nid','0'))
        if nid:
            if node_nName and node_nUrl:
                if node_nType == 'N':
                    if not node_subhead:
                        self.get_error('javascript:history.go(-1);','10',u'分类不能为空','toaza.com')
                        return

                Node().node_admin_update(node_nName,node_nUrl,node_nDes,node_nType,node_subhead,nid)
                self.logaw('admin',u'修改节点','0','0',nid,'0') #记录日志(type,des,aid,cid,nid,puid)
                self.get_error('javascript:history.go(-2);','10',u'修改成功','toaza.com')
            else:
                self.get_error('javascript:history.go(-1);','10',u'名字和url不能为空','toaza.com')
                return
        else:
            if node_nName and node_nUrl:
                if node_nType == 'N':
                    if not node_subhead:
                        self.get_error('javascript:history.go(-1);','10',u'分类不能为空','toaza.com')
                        return
                check_node_url = Node().find_by_nType_and_nUrl_and_nName('N',node_nUrl,node_nName)
                if not check_node_url:
                    nodeid = Node().node_admin_new(node_nName,node_nUrl,node_nDes,node_nType,node_subhead)
                    self.logaw('admin',u'添加节点','0','0',nodeid,'0') #记录日志(type,des,aid,cid,nid,puid)
                    if nodeid:
                        if node_nType == 'N':
                            self.get_error('/zzginoa/nodes?op=index&nType=N','10',u'节点添加成功','toaza.com')
                            return
                        else:
                            self.get_error('/zzginoa/nodes?op=index&nType=C','10',u'分类添加成功','toaza.com')
                            return
                    else:
                        self.get_error('javascript:history.go(-1);','10',u'添加出错','toaza.com')
                        return
                else:
                    self.get_error('javascript:history.go(-1);','10',u'节点名称、Url已经存在','toaza.com')
                    return
            else:
                self.get_error('javascript:history.go(-1);','10',u'名字、url不能为空','toaza.com')
                return

class zz_users(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        if self.session['gnaflag'] <> '675':
            raise tornado.web.HTTPError(404)
            return

        try:
            op = xhtml_escape(self.get_argument('op','index'))
            pageid = int(self.get_argument("p",1))
            uid = int(self.get_argument('uid','0'))
            uflag = int(self.get_argument("norclo",'1'))
        except:
            self.get_error('/zzginoa/users','10',u'error','toaza.com')
            return

        if op == 'index':
            uTotal = User().where('flag','!=',uflag).count()
            if uTotal:
                if uTotal % adminpnum == 0:
                    pages = uTotal / adminpnum
                else:
                    pages = uTotal / adminpnum + 1
                offset = (pageid - 1) * adminpnum
                userlists = []
                users = User().where('flag','!=',uflag).findall(limit=adminpnum,offset=offset)
                for u in users:
                    u = u.to_dict()
                    if u.item:
                        u.item = pickle_loads(str(u.item))
                    else:
                        u.item = ''
                    u.flag = checkuserflag(str(u.flag))
                    userlists.append(u)

                countent = self.render_template('zz_users.html',
                    users = userlists,
                    f1page = '/zzginoa/users?op=%s&amp;norclo=%s'%(str(op),uflag),
                    f1pagewa = '&',
                    thisp = pageid,
                    Totalp = pages,
                    uTotal = uTotal,
                    title = u'用户管理',)
                self.write(countent)
        elif op == 'doclock':
            if uid:
                if uid == 1:
                    self.get_error('javascript:history.go(-1);','2',u'该用户不能锁定','toaza.com')
                    return
                else:
                    User().update_user_flag('2',uid)
                    self.logaw('admin',u'锁定用户','0','0','0',uid) #记录日志(type,des,aid,cid,nid,puid)
                    self.get_error('javascript:history.go(-1);','2',u'用户已锁定','toaza.com')
                    return
            else:
                self.get_error('/zzginoa/users','2',u'error','toaza.com')
                return
        elif op == 'dounclock':
            if uid:
                if uid == 1:
                    self.get_error('javascript:history.go(-1);','2',u'该用户不能解锁','toaza.com')
                    return
                else:
                    User().update_user_flag('1',uid)
                    self.logaw('admin',u'解锁用户','0','0','0',uid) #记录日志(type,des,aid,cid,nid,puid)
                    self.get_error('javascript:history.go(-1);','2',u'用户已解锁','toaza.com')
                    return
            else:
                self.get_error('/zzginoa/users','2',u'error','toaza.com')
                return
        elif op == 'edit':
            if uid:
                user = User().select(['uid','username']).find_by_uid(uid)
                countent = self.render_template('zz_users_edit.html',
                    user = user,
                    title = u'编辑 - 用户管理',)
                self.write(countent)
            else:
                self.get_error('/zzginoa/users','2',u'error','toaza.com')
                return
        else:
            self.get_error('/zzginoa/users','10',u'参数错误','toaza.com')
            return

    @tornado.web.authenticated
    def post(self):
        if self.session['gnaflag'] <> '675':
            raise tornado.web.HTTPError(404)
            return

        try:
            username = unicode(xhtml_escape(self.get_argument('username', '').strip()))
            uid = int(self.get_argument('uid', '0').strip())
        except:
            self.get_error('/zzginoa/users','10',u'error','toaza.com')
            return

        user = User().select(['uid']).find_by_username(username)
        if user:
            self.get_error('javascript:history.go(-1);','2',u'用户名已经存在','toaza.com')
            return
        else:
            User().update_only_username(username,uid)
            self.logaw('admin',u'修改用户','0','0','0',uid) #记录日志(type,des,aid,cid,nid,puid)
            self.get_error('javascript:history.go(-1);','3',u'修改成功','toaza.com')
            return

class zz_logs(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        if self.session['gnaflag'] <> '675':
            raise tornado.web.HTTPError(404)
            return

        pageid = int(self.get_argument("p",1))
        op = xhtml_escape(self.get_argument('op', 'index'))
        access_token = str(self.get_cookie('_part',''))
        token = self.get_argument('token', '0')

        if op == 'index':
            aTotal = Log().count()
            if aTotal:
                if aTotal % adminpnum == 0:
                    pages = aTotal / adminpnum
                else:
                    pages = aTotal / adminpnum + 1
                offset = (pageid-1) * adminpnum
                logs = []
                lids = Log().order_by('-optime').findall(adminpnum,offset)
                for li in lids:
                    uid = User().select(['username']).find_by_uid(li.uid).to_dict()
                    aid = Article().select(['title']).find_by_aid(li.aid).to_dict()
                    pun = User().select(['(username) as puname']).find_by_uid(li.puid)
                    nid = Node().select(['nName','nUrl']).find_by_nid(li.nid).to_dict()
                    arts = uid.copy()
                    arts.update(li.to_dict())
                    arts.update(aid)
                    arts.update(pun)
                    arts.update(nid)
                    logs.append(arts)

                countent = self.render_template('zz_logs.html',
                    logs = logs,
                    f1page = '/zzginoa/logs',
                    f1pagewa = '?',
                    thisp = pageid,
                    Totalp = pages,
                    aTotal = aTotal,
                    access_token = access_token,
                    title = u'日志管理',)
                self.write(countent)
        elif op == 'del:login':
            if token != access_token:
                self.get_error('/','10',u'参数异常',SITE_NAME)
                return
            adminlid =  Log().findall_by_optype('login',limit=Log().where('optype','=','login').count())
            for ali in adminlid:
                ali.delete()
            self.logaw('admin',u'删除登录日志','0','0','0','0')  #记录日志(type,des,aid,cid,nid,puid)
            self.get_error('/zzginoa/logs','10',u'删除完成',SITE_NAME)
            return
        else:
            self.get_error('/','10',u'参数错误','toaza.com')
            return