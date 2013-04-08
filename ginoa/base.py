#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# base
# toaza.com
#
import os.path
import tornado.web
from helpers import setdateo,temptime,generate_random,content_formate,nl2br,pickle_loads
from extensions.sessions import Session
from jinja2 import Environment, FileSystemLoader,FileSystemBytecodeCache
from site_sitting import *
from tornado.escape import xhtml_escape
from model.testm import Log,Commentreid,User # db model (sqlalchemy)

class RequestHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        userid = self.session['gnauid'] if 'gnauid' in self.session else None
        if not self.get_cookie('_part',''):
            self.set_cookie('_part',generate_random(),expires_days=300)
        return userid

    def render_template(self,filename, **context):
        gnaflag = self.session['gnaflag'] if 'gnaflag' in self.session else ''
        gnauid = self.session['gnauid'] if 'gnauid' in self.session else ''
        gnaname = self.session['gnaname'] if 'gnaname' in self.session else ''
        access_token = self.get_cookie('_part','')

        if gnauid:
            atuid_count = Commentreid().where('checked','=','0').count_by_uid(gnauid)
            authorinfo = User().select(['username','item','isavatar','isnofrist']).find_by_uid(gnauid)
            if authorinfo and authorinfo.item:
                authorinfo.item = pickle_loads(str(authorinfo.item))
            else:
                authorinfo.item = ''
        else:
            atuid_count = '0'
            authorinfo = ''

        extensions = context.pop('extensions', [])
        globals = context.pop('globals', {})
        jinja_env = Environment(
            loader = FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates').replace('\\','/')),
            extensions = extensions,
            bytecode_cache = FileSystemBytecodeCache('/tmp', '%s.jinja2.toaza'),
            cache_size = 50,
            #encoding = 'utf-8',
            autoescape = False,
            finalize = None,
            optimized = True,
            auto_reload = True, #None
            trim_blocks = True
        )
        # add filters
        jinja_env.filters['setdateo'] = setdateo #时间戳转换
        jinja_env.filters['content_formate'] = content_formate #格式化文本
        jinja_env.filters['nl2br'] = nl2br #格式化文本
        jinja_env.globals.update(globals)
        context.update({
            'gnaname' : gnaname,
            'gnaflag' : gnaflag,
            'gnauid' : gnauid,
            'user_c_info': authorinfo,
            'xsrf_form_html' : self.xsrf_form_html,
            'request' : self.request,
            #'current_user' : self.current_user,
            'SITE_NAME' : SITE_NAME,
            'imgUrl' : AVATAR_URL,
            'statUrl' : STATIC_URL,
            'SITE_VERSION' : SITE_VERSION,
            'atuid_count':atuid_count,
            'access_token':access_token,
        })
        return jinja_env.get_template(filename).render(context)#.decode('utf-8')

    @property
    def session(self):
        if hasattr(self, '_session'):
            return self._session
        else:
            expires = PERMANENT_SESSION_LIFETIME or None
            self._session = Session(self.get_secure_cookie, self.set_secure_cookie, expires_days=expires)
            return self._session

    def get_error(self,tourl='/', wmin='2',msga='error',msgalt='error', **countent):
        tourl = xhtml_escape(tourl.strip())
        wmin = int(wmin)
        msga = unicode(xhtml_escape(msga.strip()))
        msgalt = unicode(xhtml_escape(msgalt.strip()))

        self.set_status(404)
        countent = self.render_template('_redirect.html',tourl = tourl,msga = msga,wmin = wmin,msgalt = msgalt,)
        self.write(countent)
        return
    
    @tornado.web.asynchronous
    def logaw(self,optype,des=None,aid=0,cid=0,nid=0,puid=0):
        # uid,optime,ipadds,optype,des,aid,cid
        # 记录日志(type,des,aid,cid,nid,puid)
        gnauid = self.session['gnauid'] if 'gnauid' in self.session else ''
        return Log().log_new(gnauid,temptime(),self.request.remote_ip,optype,des,aid,cid,nid,puid)

class ErrorHandler(RequestHandler):
    # raise 404 error if url is not found. fixed tornado.web.RequestHandler HTTPError bug.
    def prepare(self):
        self.set_status(404)
        raise tornado.web.HTTPError(404)


