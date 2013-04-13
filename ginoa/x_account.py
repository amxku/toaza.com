#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# account
# toaza.com
#
import tornado.auth
from base import RequestHandler
from helpers import pickle_dumps, pickle_loads
from tornado.escape import xhtml_escape
from site_sitting import *
from extensions.upyun import UpYun
from model.authmixin import WeiboMixin
from model.testm import User, Article, Log, Commentreid, Comment, Noderelated, Node
# db model (sqlalchemy)


# 退出
class signout(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        del self.session['gnauid']
        del self.session['gnaname']
        del self.session['gnaflag']
        self.session.save()
        self.redirect(self.get_argument("next", "/"))


# 账号登录
#todo 账号合并
class signin(RequestHandler):
    def get(self):
        title = u'用户登录'
        countent = self.render_template('user_login.html', title=title,)
        self.write(countent)


# sina用户登录
class signin_sina(RequestHandler, WeiboMixin):
    @tornado.web.asynchronous
    def get(self):
        if CHECK_LOGIN == 1:
            next = self.get_argument("next", None)
            redirect_uri = SINA_redirect_uri
            code = self.get_argument("code", None)

            if not code:
                self.authorize_redirect(
                    redirect_uri=redirect_uri,
                    client_id=SINA_CONSUMER_KEY,
                    extra_params={"response_type": "code", "state": next},
                )

        else:
            self.get_error('/', '10', u'系统禁止登录', SITE_NAME)


#sina callback
class sina_callbackpage(RequestHandler,WeiboMixin):
    @tornado.web.asynchronous
    def get(self):
        state = self.get_argument("state", None)
        code = self.get_argument("code", None)
        redirect_uri = SINA_redirect_uri

        self.get_authenticated_user(
            redirect_uri = redirect_uri,
            client_id = SINA_CONSUMER_KEY,
            client_secret = SINA_CONSUMER_SECRET,
            code = code,
            callback = self.async_callback(self._on_login,state))
        return

    def _on_login(self,next, user):
        if not user:
            self.get_error('/','10',u'Sina auth failed',SITE_NAME)
            return

        author = User().select(['uid','username','flag']).find_by_sinaid(user['id'])
        if not author:
            if CHECK_REG == 1:
                userid = User().user_new_sina(user['screen_name'],user['id'],'1')
                self.session['gnauid'] = userid
                self.session['gnaname'] = user['screen_name']
                self.session['gnaflag'] = '1'
                self.session.save()
                self.logaw('reg',u'注册(第一次登录)','0','0','0','0') #记录日志(type,des,aid,cid,nid,puid)
                self.redirect('/settings')
            else:
                self.get_error('/','10',u'系统禁止注册',SITE_NAME)
                return
        else:
            self.session['gnauid'] = author.uid
            self.session['gnaname'] = author.username
            self.session['gnaflag'] = author.flag
            self.session.save()
            self.logaw('login',u'登录','0','0','0','0') #记录日志(type,des,aid,cid,nid,puid)
            self.redirect(next)

# google用户登录
class signin_google(RequestHandler, tornado.auth.GoogleMixin):
    _OPENID_ENDPOINT = "https://www.google.com.tw/accounts/o8/ud"
    _OAUTH_ACCESS_TOKEN_URL = "https://www.google.com.tw/accounts/OAuthGetAccessToken"

    @tornado.web.asynchronous
    def get(self):
        if CHECK_LOGIN == 1:
            if self.get_argument("openid.mode", None):
                self.get_authenticated_user(self.async_callback(self._on_auth))
                return
            self.authenticate_redirect()
        else:
            self.get_error('/','10',u'系统禁止登录',SITE_NAME)

    def _on_auth(self, user):
        if not user:
            self.get_error('/','10',u'Google auth failed',SITE_NAME)
            return

        author = User().select(['uid','username','flag']).find_by_email(user["email"])
        if not author:
            if CHECK_REG == 1:
                usermail = xhtml_escape(user["email"].strip())
                username =  xhtml_escape(usermail.split('@')[0])
                userid = User().user_new_google(username,usermail,'1')
                self.session['gnauid'] = userid
                self.session['gnaname'] = username
                self.session['gnaflag'] = '1'
                self.session.save()
                self.logaw('reg',u'注册(第一次登录)','0','0','0','0') #记录日志(type,des,aid,cid,nid,puid)
                self.redirect('/settings')
            else:
                self.get_error('/','10',u'系统禁止注册',SITE_NAME)
        else:
            self.session['gnauid'] = author.uid
            self.session['gnaname'] = author.username
            self.session['gnaflag'] = author.flag
            self.session.save()
            self.logaw('login',u'登录','0','0','0','0') #记录日志(type,des,aid,cid,nid,puid)
            self.redirect(self.get_argument('next', '/'))

#个人信息设置
class authset(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        countent = self.render_template('user_settings.html',
            title = u'设置',)
        self.write(countent)

    @tornado.web.authenticated
    def post(self):
        username = unicode(xhtml_escape(self.get_argument('username', '').strip()))
        website = unicode(xhtml_escape(self.get_argument('website', '').strip()))
        location = unicode(xhtml_escape(self.get_argument('location', '').strip()))
        tagline = unicode(xhtml_escape(self.get_argument('tagline', '').strip()))
        bio = unicode(xhtml_escape(self.get_argument('bio', '').strip()))
        gnauid = self.session['gnauid'] if 'gnauid' in self.session else ''

        if username:
            # username isalnum
            if not username.isalnum():
                self.get_error('javascript:history.go(-1);','2',u'用户名，请使用半角的字母或数字',u'点击返回修改')
                return

            # username len
            if len(username) >16 or len(username) <3:
                self.get_error('javascript:history.go(-1);','2',u'用户名长度不能超过16个字符、小于3个字符',u'点击返回修改')
                return

        if tagline and len(tagline) >32:
            self.get_error('javascript:history.go(-1);','2',u'签名不能超过 32 个字符',u'点击返回修改')
            return

        userinfolist = {'website':website,'location':location,'tagline':tagline,'bio':bio}
        itemcp = pickle_dumps(userinfolist)
        if username:
            check_username = User().select(['uid']).find_by_username(username)
            if check_username and check_username.uid != gnauid:
                self.get_error('/settings','5',u'该用户名已被占用，请修改后提交',SITE_NAME)
                return
            else:
                User().update_user_name(itemcp,username,'F',gnauid)
                del self.session['gnaname']
                self.session['gnaname'] = username
                self.session.save()
                self.logaw('setting',u'设置个人信息','0','0','0','0') #记录日志(type,des,aid,cid,nid,puid)
        else:
            User().update_user(itemcp,'T',gnauid)
            self.logaw('setting',u'设置个人信息','0','0','0','0') #记录日志(type,des,aid,cid,nid,puid)
        self.redirect('/settings')

#查看用户信息
class view_user(RequestHandler):
    def get(self,username):
        username = xhtml_escape(username.strip())
        if username:
            authorinfo = User().select(['uid','username','item','isavatar','regtime']).find_by_username(username)
            if authorinfo:
                if authorinfo.item:
                    authorinfo.item = pickle_loads(str(authorinfo.item))
                else:
                    authorinfo.item = ''

                logs = []
                anodes = []
                typelists = ['article','comments']
                aidlists = []
                lids = Log().select(['aid','optime','optype','cid']).order_by('-optime').where('uid','=',authorinfo.uid).findall_in_optype(typelists,limit=15)
                for li in lids:
                    aids = Article().select(['title']).find_by_aid(li.aid).to_dict()
                    cids = Comment().select(['content']).find_by_cid(li.cid).to_dict()
                    arts = aids.copy()
                    arts.update(li.to_dict())
                    arts.update(cids)
                    logs.append(arts)
                    aidlists.append(li.aid)

                aidlis = {}.fromkeys(aidlists).keys()#list 去重复
                anode = Noderelated().select(['nid','aid']).findall_in_aid(aidlis)
                for anid in anode:
                    anids = Node().select(['nName','nUrl']).find_by_nid(anid.nid).to_dict()
                    nrts = anids.copy()
                    nrts.update(anid.to_dict())
                    anodes.append(nrts)

                countent = self.render_template('user_view.html',
                    title = username + ' - ' + SITE_NAME,
                    authorinfo = authorinfo,
                    logs = logs,
                    anodes = anodes,
                    useravatar = authorinfo.uid,)
                self.write(countent)
            else:
                self.get_error('/','10',u'没有找到',SITE_NAME)
        else:
            self.get_error('/','10',u'参数错误',SITE_NAME)

# 头像上传
class avatarupload(RequestHandler):
    @tornado.web.authenticated
    def post(self):
        myfile = self.request.files.get('avatar',[0])[0]
        if myfile:
            u = UpYun(DOMAIN_NAME_AVATAR, UPYUN_USER, UPYUN_PW)
            file_path_name = '/theones/avatar/%s.png'% self.session['gnauid']
            avatar = u.writeFile(file_path_name, myfile['body'], True)
            if not avatar:
                self.get_error('/settings','5',u'保存图片出错，请稍后再试',SITE_NAME)
            else:
                User().update_avatar(self.session['gnauid'])
                self.logaw('avatar',u'上传头像','0','0','0','0') #记录日志(type,des,aid,cid,nid,puid)
                self.redirect('/settings#avatar')
        else:
            self.get_error('/settings','5',u'图片没有正确上传',SITE_NAME)

# 消息提醒
class alerts(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        gnauid = self.session['gnauid'] if 'gnauid' in self.session else ''
        lids = []
        crid = Commentreid().select(['lid','atype','crid']).order_by('-crid').findall_by_uid(gnauid,limit=100)
        for cri in crid:
            logds = Log().select(['aid','cid','optime','uid']).where('optype','=','comments').find_by_lid(cri.lid).to_dict()
            userds = User().select(['username','isavatar']).find_by_uid(logds.uid).to_dict()
            articleds = Article().select(['title']).find_by_aid(logds.aid).to_dict()
            iai = cri.to_dict()
            arts = logds.copy()
            arts.update(iai)
            arts.update(userds)
            arts.update(articleds)
            lids.append(arts)

            Commentreid().check_alerts_by_uid(cri.crid)
        title = u'提醒消息'
        countent = self.render_template('user_alerts.html',
            title = title,
            lids = lids,)
        self.write(countent)

#删除提醒消息
class alertsdel(RequestHandler):
    @tornado.web.authenticated
    def get(self):
        crid = int(self.get_argument('id', '0'))
        token = self.get_argument('token', '0')
        access_token = str(self.get_cookie('_part',''))
        if token != access_token:
            self.get_error('/','10',u'参数异常',SITE_NAME)
            return
        if crid:
            crds = Commentreid().select(['uid', 'crid']).find_by_crid(crid)
            if crds:
                if self.session['gnauid'] == crds.uid:
                    crds.delete()
                    self.logaw('setting', u'删除提醒消息', '0', crds.crid, '0', '0')
                    #记录日志(type,des,aid,cid,nid,puid)
                    self.get_error('/user:alerts','4',u'删除成功',SITE_NAME)
                    return
                else:
                    self.get_error('/', '4', u'error', SITE_NAME)
                    return
            else:
                self.get_error('/', '10', u'参数异常', SITE_NAME)
                return
        else:
            self.get_error('/', '4', u'error', SITE_NAME)
            return
