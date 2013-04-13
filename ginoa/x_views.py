#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# articles views
# toaza.com
#
import tornado.auth
from tornado.escape import xhtml_escape
from base import RequestHandler
from site_sitting import *
from helpers import temptime, clear2nbsp, get_cache, findall_mentions, pickle_loads
from model.testm import User, Article, Comment, Node, Noderelated, Log, Commentreid
# db model (sqlalchemy)


# /index
class main_index(RequestHandler):
    def get(self):
        gnauid = self.session['gnauid'] if 'gnauid' in self.session else ''

        annids = []
        anodeids = []
        aarticles = Article().select(['uid', 'aid', 'title', 'lastctime', 'comtotal']).order_by('-lastctime').findall(limit=pnum)
        for iai in aarticles:
            auser = User().select(['username', 'isavatar']).find_by_uid(iai.uid).to_dict()
            iai = iai.to_dict()
            arts = auser.copy()
            arts.update(iai)
            anodeids.append(arts)

            anode = Noderelated().select(['nid', 'aid']).findall_by_aid(iai.aid)
            for anid in anode:
                anid = anid.to_dict()
                anids = Node().select(['nName', 'nUrl']).find_by_nid(anid.nid).to_dict()
                artsn = anid.copy()
                artsn.update(anids)
                annids.append(artsn)

        results_user_counter = User().count()
        results_article_counter = Article().count()
        results_comments_counter = Comment().count()
        nodens = Node().select(['nName', 'nUrl', 'subhead']).order_by('-nCou').where('nCou', '!=', '0').where('subhead', '!=', '0').where('nType', '=', 'N').findall(limit=node_total)

        #cache
        if not gnauid:
            anodeids = get_cache('index_articles', anodeids, timeout=60*5)

        results_user_counter = get_cache('results_user_counter', results_user_counter, timeout=60*30)
        results_article_counter = get_cache('results_article_counter', results_article_counter, timeout=60*30)
        results_comments_counter = get_cache('results_comments_counter', results_comments_counter, timeout=60*30)

        countent = self.render_template('home.html',
                                        title=SITE_NAME,
                                        articles=anodeids,
                                        nodens=nodens,
                                        nodes=annids,
                                        user_Count=results_user_counter,
                                        article_Count=results_article_counter,
                                        comments_Count=results_comments_counter,)
        self.write(countent)


# /recent?p=
class listrecent(RequestHandler):
    def get(self):
        try:
            pageid = int(self.get_argument("p", 1))
        except:
            self.get_error('/', '10', u'参数错误', SITE_NAME)
            return

        results_user_counter = User().count()
        results_article_counter = Article().count()
        results_comments_counter = Comment().count()

        aTotal = Article().count()
        if aTotal:
            if aTotal % pnum == 0:
                pages = aTotal / pnum
            else:
                pages = aTotal / pnum + 1
            offset = (pageid-1) * pnum

            anodeids = []
            annids = []
            aarticles = Article().select(['uid', 'aid', 'title', 'lastctime', 'comtotal']).order_by('-lastctime').findall(limit=pnum, offset=offset)
            for iai in aarticles:
                auser = User().select(['username', 'isavatar']).find_by_uid(iai.uid).to_dict()
                iai = iai.to_dict()
                arts = auser.copy()
                arts.update(iai)
                anodeids.append(arts)

                anode = Noderelated().select(['nid', 'aid']).findall_by_aid(iai.aid)
                for anid in anode:
                    anid = anid.to_dict()
                    anids = Node().select(['nName', 'nUrl']).find_by_nid(anid.nid).to_dict()
                    artsn = anid.copy()
                    artsn.update(anids)
                    annids.append(artsn)

        else:
            self.get_error('/', '10', u'参数错误', SITE_NAME)
            return

        countent = self.render_template('view_pages.html',
                                        title=u'最近的推帖 %s/%s - %s' % (pageid, pages, SITE_NAME),
                                        nodes=annids,
                                        articles=anodeids,
                                        f1page='/recent',
                                        f1pagewa='?',
                                        thisp=pageid,
                                        Totalp=pages,
                                        user_Count=results_user_counter,
                                        article_Count=results_article_counter,
                                        comments_Count=results_comments_counter,)
        self.write(countent)


# /n/*
class nlists(RequestHandler):
    def get(self, nName):
        try:
            gnName = xhtml_escape(nName)
            pageid = int(self.get_argument("p", 1))
        except:
            self.get_error('/', '10', u'error', SITE_NAME)
            return
        nodenid = Node().select(['nName', 'nDes', 'nid', 'nUrl']).find_by_nUrl(gnName)
        if nodenid:
            aTotal = Noderelated().count_by_nid(nodenid.nid)
            if aTotal:
                if aTotal % pnum == 0:
                    pages = aTotal / pnum
                else:
                    pages = aTotal / pnum + 1
                offset = (pageid-1) * pnum

                nrids = []
                anodeids = []
                naids = Noderelated().select(['aid']).findall_by_nid(nodenid.nid, limit=pnum, offset=offset)
                for nir in naids:
                    nrids.append(nir.aid)
                aarticles = Article().select(['uid', 'aid', 'title', 'aptime', 'comtotal']).findall_in_aid(nrids)
                for iai in aarticles:
                    auser = User().select(['username', 'isavatar']).find_by_uid(iai.uid).to_dict()
                    iai = iai.to_dict()
                    arts = auser.copy()
                    arts.update(iai)
                    anodeids.append(arts)

                if pageid == 1:
                    title = nodenid.nName + ' - ' + SITE_NAME
                else:
                    title = '%s %s/%s - %s' % (nodenid.nName, pageid, pages, SITE_NAME)

                countent = self.render_template('view_tag.html',
                                                title=title,
                                                nodenid=nodenid,
                                                f1page='/n/' + nodenid.nUrl,
                                                f1pagewa='?',
                                                thisp=pageid,
                                                Totalp=pages,
                                                narticles=anodeids,)
                self.write(countent)
            else:
                self.get_error('/', '10', u'None', SITE_NAME)
                return
        else:
            self.get_error('javascript:history.go(-1);', '10', u'没找到哦', u'点击返回')
            return


# /a/*
class ashow(RequestHandler):
    def get(self, aid):
        try:
            aid = int(aid)
        except:
            self.get_error('/', '10', u'None', SITE_NAME)
            return

        articlei = Article().find_by_aid(aid)
        if articlei:
            ausers = User().select(['username', 'isavatar']).find_by_uid(articlei.uid)
            comas = []
            annids = []
            anode = Noderelated().select(['nid']).findall_by_aid(articlei.aid)
            for anid in anode:
                anid = anid.to_dict()
                anids = Node().select(['nName', 'nUrl']).find_by_nid(anid.nid).to_dict()
                artsn = anid.copy()
                artsn.update(anids)
                annids.append(artsn)

            comment = Comment().order_by('cptime').findall_by_aid(aid, limit=comm_total)
            for ci in comment:
                cuser = User().select(['username', 'isavatar', 'item']).find_by_uid(ci.uid).to_dict()
                iai = ci.to_dict()
                arts = cuser.copy()
                arts.update(iai)
                comas.append(arts)

            for cidi in comas:
                if cidi and cidi['item']:
                    cidi['item'] = pickle_loads(str(cidi['item']))
                else:
                    cidi['item'] = ''

            countent = self.render_template('view_article.html',
                                            title=unicode(articlei.title) + ' - ' + SITE_NAME,
                                            article=articlei,
                                            comments=comas,
                                            auser=ausers,
                                            nodes=annids,
                                            nowtime=temptime(),)
            self.write(countent)
        else:
            self.get_error('/', '10', u'参数错误', SITE_NAME)


# 添加评论
class newcomment(RequestHandler):
    @tornado.web.authenticated
    def post(self):
        gnauid = self.session['gnauid'] if 'gnauid' in self.session else ''
        uinfo = User().select(['isnofrist']).find_by_uid(gnauid)
        if uinfo.isnofrist == 'F':
            self.get_error('/settings', '10', u'您还没有设置用户名', SITE_NAME)
            return
        if self.session["gnaflag"] == '2':
            self.get_error('/', '10', u'您的账户被锁定', SITE_NAME)
            return

        aid = int(self.get_argument('aid', ''))
        #获取主题ID
        if aid:
            arts = Article().select(['uid']).find_by_aid(aid)
            if arts:
                comment = xhtml_escape(self.get_argument('comment', '').strip())
                if len(comment) < 4:
                    self.get_error('javascript:history.go(-1);', '5', u'输入的字符不能小于4个字符', SITE_NAME)
                    return

                tourl = '/a/' + str(aid)
                if comment:
                    user_i = User().select(['uid']).find_by_uid(gnauid)
                    comid = Comment().comment_new(user_i.uid, aid, comment, temptime())
                    Article().article_comcount(temptime(), aid)
                    #更新回复数量

                    logid = self.logaw('comments', u'回复评论', aid, str(comid), '0', '0')
                    #记录日志(type,des,aid,cid,nid,puid)
                    ##消息提醒################################################################
                    #排除自己
                    at_users = findall_mentions(comment)
                    if at_users:
                        for atu in at_users:
                            atuid = User().select(['uid']).find_by_username(atu)
                            if str(atuid.uid) != str(gnauid):
                                Commentreid().commentr_new(atuid.uid, logid, '0')
                    else:
                        if str(arts.uid) != str(gnauid):
                            Commentreid().commentr_new(arts.uid, logid, '1')
                    ##消息提醒##################################################################
                    self.redirect(tourl + '#reply' + str(comid))
                else:
                    self.get_error(tourl, '10', u'参数异常', SITE_NAME)
                    return
            else:
                self.get_error('/', '10', u'参数异常', SITE_NAME)
                return
        else:
            self.get_error('/', '10', u'参数异常', SITE_NAME)
            return


#添加新主题
class newpost(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        gnauid = self.session['gnauid'] if 'gnauid' in self.session else ''
        uinfo = User().select(['isnofrist']).find_by_uid(gnauid)
        if uinfo.isnofrist == 'F':
            self.get_error('/settings', '10', u'您还没有设置用户名', SITE_NAME)
            return

        if self.session["gnaflag"] == '2':
            self.get_error('/', '10', u'您的账户被锁定', SITE_NAME)
            return

        access_token = str(self.get_cookie('_part', ''))
        token = self.get_argument('token', '0')
        if token != access_token:
            self.get_error('/', '10', u'参数异常', SITE_NAME)
            return

        tagsnodes = Node().select(['nName']).where('nType', '=', 'N').order_by('-nid').findall(limit=Node().where('nType', '=', 'N').count())
        aid = self.get_argument('id', '')
        #获取主题ID
        if aid:
            #编辑主题
            nnodeid = ''
            aarticles = Article().select(['uid', 'aid', 'title', 'aptime', 'content']).find_by_aid(aid)
            if (aarticles.uid == self.session['gnauid'] and temptime() - aarticles.aptime < 1800) or self.session['gnaflag'] == '675':
                articlee = aarticles
                nodes = []
                anode = Noderelated().select(['nid', 'aid']).findall_by_aid(aid)
                for anid in anode:
                    anid = anid.to_dict()
                    anids = Node().select(['nName', 'nUrl']).find_by_nid(anid.nid).to_dict()
                    artsn = anid.copy()
                    artsn.update(anids)
                    nodes.append(artsn)

                if not nodes:
                    nodes = ''
                atitle = u'编辑'
            else:
                self.redirect('/')
                return
        else:
            articlee = None
            atitle = u'推新帖'
            nodes = None
            nnodeid = self.get_argument('n', '')

        countent = self.render_template('view_newpost.html',
                                        title=unicode(atitle),
                                        nnodeid=nnodeid,
                                        nodes=nodes,
                                        tagsnodes=tagsnodes,
                                        articlee=articlee,)
        self.write(countent)

    @tornado.web.authenticated
    def post(self):
        gnauid = self.session['gnauid'] if 'gnauid' in self.session else ''
        uinfo = User().select(['isnofrist']).find_by_uid(gnauid)
        if uinfo.isnofrist == 'F':
            self.get_error('/settings', '10', u'您还没有设置用户名', SITE_NAME)
            return
        if self.session["gnaflag"] == '2':
            self.redirect(self.get_argument("next", "/"))
            return

        title = unicode(xhtml_escape(self.get_argument('title', '').strip()))
        content = xhtml_escape(self.get_argument('content', '').strip())
        tags = unicode(xhtml_escape(self.get_argument('atag', '').strip().replace(',,', ',').strip(',')))

        # title 长度
        if len(title) > 120:
            self.get_error('javascript:history.go(-1);', '2', u'标题太长了点', u'点击返回修改')
            return

        aid = self.get_argument('id', '')
        #获取主题ID
        if aid:
            #编辑主题
            tourl = '/a/' + str(aid)
            articlei = Article().select(['uid', 'aid', 'title', 'aptime', 'content']).find_by_aid(aid)
            #判断权限
            if (self.session['gnauid'] == articlei.uid and temptime() - articlei.aptime < 1800) or self.session['gnaflag'] == '675':
                if articlei:
                    if not tags:
                        Noderelated().findall_by_aid(aid).delete()
                        self.get_error('javascript:history.go(-1);', '2', u'节点不能为空', u'点击返回修改')
                        return
                    else:
                        old_nodeid = Noderelated().select(['nrid']).findall_by_aid(aid)
                        for oid in old_nodeid:
                            oid.delete()

                        atags = tags.split(",")
                        if not atags[0]:
                            self.get_error('javascript:history.go(-1);', '2', u'节点不能为空', u'点击返回修改')
                            return

                        for atg in atags:
                            if atg:
                                atag = Node().select(['nid']).find_by_nName(atg)
                                if atag:
                                    checnnodeid = Noderelated().find_by_aid_and_nid(aid, atag.nid)
                                    if not checnnodeid:
                                        Noderelated().noderelated_new(aid, atag.nid)
                                else:
                                    nnid = Node().node_new(atg, clear2nbsp(atg).lower())
                                    checnnodeid = Noderelated().find_by_aid_and_nid(aid, nnid)
                                    if not checnnodeid:
                                        Noderelated().noderelated_new(aid, nnid)
                            else:
                                pass

                    Article().article_edit(title, content, aid)
                    self.logaw('editarticle', u'修改主题', aid, '0', '0', '0')
                    #记录日志(type,des,aid,cid,nid,puid)
                    self.redirect(tourl)
                else:
                    self.get_error('/', '10', u'参数异常', SITE_NAME)
                    return
            else:
                self.get_error('/', '4', u'发布时间已经超过30分钟，禁止修改', SITE_NAME)
                return
        else:
            #提交新主题
            checkaid = Article().select(['aid']).find_by_title(title)
            if not checkaid:
                atags = tags.split(",")
                if not atags[0]:
                    self.get_error('javascript:history.go(-1);', '2', u'节点不能为空', u'点击返回修改')
                    return
                else:
                    atags = tags.split(",")
                    if not atags[0]:
                        self.get_error('javascript:history.go(-1);', '2', u'节点不能为空', u'点击返回修改')
                        return

                    aid = Article().article_new(self.session['gnauid'], title, content, temptime(), temptime())
                    self.logaw('article', u'新主题', aid, '0', '0', '0')
                    #记录日志(type,des,aid,cid,nid,puid)
                    for atg in atags:
                        if atg:
                            atag = Node().select(['nid']).find_by_nName(unicode(atg))
                            if atag:
                                checnnodeid = Noderelated().find_by_aid_and_nid(aid, atag.nid)
                                if not checnnodeid:
                                    Noderelated().noderelated_new(aid, atag.nid)
                            else:
                                if len(atag) < 2:
                                    pass
                                    #丢弃小于2个字节的tag
                                else:
                                    nnid = Node().node_new(atg, clear2nbsp(atg).lower())
                                    checnnodeid = Noderelated().find_by_aid_and_nid(aid, nnid)
                                    if not checnnodeid:
                                        Noderelated().noderelated_new(aid, nnid)
                        else:
                            pass
                tourl = '/a/' + str(aid)
                self.redirect(tourl)
            else:
                self.get_error('javascript:history.go(-1);', '4', u'标题已经存在，请修改', u'点击返回修改')
                return


#删除主题
class delpost(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        aid = int(self.get_argument('id', '0'))
        token = self.get_argument('token', '0')
        access_token = str(self.get_cookie('_part', ''))
        if token != access_token:
            self.get_error('/', '10', u'参数异常', SITE_NAME)
            return
        if aid:
            articlei = Article().select(['uid', 'aptime']).find_by_aid(aid)
            if (self.session['gnauid'] == articlei.uid and temptime()-articlei.aptime < 1800) or self.session['gnaflag'] == '675':
                ######删除所有相关记录
                coid = Comment().select(['cid']).findall_by_aid(aid, limit=Comment().where('aid', '=', aid).count())
                for cid in coid:
                    cid.delete()
                lids = Log().select(['lid']).findall_by_aid(aid, limit=Log().where('aid', '=', aid).count())
                for lidi in lids:
                    crid = Commentreid().select(['crid']).find_by_lid(lidi.lid)
                    for crida in crid:
                        crida.delete()
                    lidi.delete()
                Article().select(['aid']).find_by_aid(aid).delete()
                ######删除所有相关记录
                self.get_error('/', '4', u'删除成功', SITE_NAME)
                return
            else:
                self.get_error('/', '4', u'error', SITE_NAME)
                return
        else:
            self.get_error('/', '4', u'error', SITE_NAME)
            return
