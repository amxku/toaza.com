#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# helpers def
# toaza.com
#
import random
from random import choice
from hashlib import sha1
import string
import re
import time
from cgi import escape
from extensions.cache import cache
from site_sitting import *
try:
    import cPickle as pickle
except ImportError:
    import pickle


def get_random():
    str_ENCODE = 'abcdefghijklmnopqrstuvwxyz0123456789'
    return ''.join(choice(str_ENCODE) for i in xrange(choice((6,7,8,9,10,11,12))))
#print get_random()

def generate_random(length=8):
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

# 取当前时间戳
def temptime():
    atime = int(time.time())
    return atime

# 加密字符
def hexuserpass(password):
    enpass = sha1(password).hexdigest()
    #enpass = sha1(password.encode('utf-8')).hexdigest()
    return enpass

# find user
def findall_mentions(text, filter_name=None):
    if '@' in text:
        ns = set([yk for yk in _re_mentions.findall(text.lower())])
        if filter_name:
            ns.discard(filter_name)
        if len(ns)<=NOTIFY_MEMBER_NUM:
            return ns
        else:
            return None
    else:
        return None

# autolink
LEADING_PUNCTUATION  = ['(', '<', '&lt;']
TRAILING_PUNCTUATION = ['.', ',', ')', '>', '\n', '&gt;']
punctuation_re = re.compile('^(?P<lead>(?:%s)*)(?P<middle>.*?)(?P<trail>(?:%s)*)$' %\
    ('|'.join([re.escape(x) for x in LEADING_PUNCTUATION]),'|'.join([re.escape(x) for x in TRAILING_PUNCTUATION])))
word_split_re = re.compile(r'(\s+)')
simple_email_re = re.compile(r'^\S+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+$')
def autolink(text, trim_url_limit=70, nofollow=True):
    # If trim_url_limit is not None, the URLs in link text will be limited to trim_url_limit characters.
    # If nofollow is True, the URLs in link text will get a rel="nofollow" attribute.
    trim_url = lambda x, limit=trim_url_limit: limit is not None and (x[:limit] + (len(x) >=limit and '...' or ''))  or x
    words = word_split_re.split(text)
    nofollow_attr = nofollow and ' rel="nofollow"' or ''
    for i, word in enumerate(words):
        match = punctuation_re.match(word)
        if match:
            lead, middle, trail = match.groups()
            if middle.startswith('www.') or ('@' not in middle and not middle.startswith('http://') and not middle.startswith('https://') and len(middle) > 0 and middle[0] in string.letters + string.digits and (middle.endswith('.org') or middle.endswith('.net') or middle.endswith('.com'))):
                middle = '<a href="http://%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle).replace(SITE_URL,''))
            if middle.startswith('http://') or middle.startswith('https://'):
                middle = '<a href="%s"%s target="_blank">%s</a>' % (middle, nofollow_attr, trim_url(middle).replace(SITE_URL,''))
            if '@' in middle and not middle.startswith('www.') and not ':' in middle and simple_email_re.match(middle):
                middle = '<a href="mailto:%s">%s</a>' % (middle, middle)
            if lead + middle + trail != word:
                words[i] = lead + middle + trail
    return ''.join(words)
# autolink end

_re_imgs = re.compile('(http[s]?://?\S*\w\.(jpg|jpe|jpeg|gif|png))\w*', re.UNICODE|re.I|re.M|re.S)
#_re_mentions = re.compile('\B\@([a-z0-9]+)', re.UNICODE|re.I|re.M|re.S)
_re_mentions = re.compile('@([a-z0-9]+)', re.UNICODE|re.I|re.M|re.S)
#http://v.youku.com/v_show/id_XNDQ4NTk5OTQw(.htm|.html)?
_re_youku = re.compile('http://v.youku.com/v_show/id_([a-zA-Z0-9\=]+)(\/|.html?)?', re.UNICODE|re.I|re.M|re.S)
#http://www.tudou.com/listplay/7cb57rueaYI/Op-E8hQrdRw(.htm|.html)?
#http://www.tudou.com/listplay/7cb57rueaYI
#http://www.tudou.com/programs/view/ro1Yt1S75bA/
_re_tudou = re.compile('http://www.tudou.com/(programs/view|listplay)/([a-zA-Z0-9\=\_\-]+)(\/|.html?)?', re.UNICODE|re.I|re.M|re.S)
#qq http://v.qq.com/boke/page/h/1/n/h04021dkn1n.html
_re_qq = re.compile('http://v.qq.com/(.+)/([a-zA-Z0-9]{8,}).(html?)', re.UNICODE|re.I|re.M|re.S)
#_re_urls = re.compile('(\w+:\/\/[^\s]+)', re.UNICODE|re.I|re.M|re.S)
_re_gist = re.compile('(https://gist.github.com/[\d]+)', re.UNICODE|re.I|re.M|re.S)
#_re_title_h2 = re.compile('(#\S*#)', re.UNICODE|re.I|re.M|re.S)
_re_title_h2 = re.compile('##([^<>\/].+?)##', re.UNICODE|re.I|re.M|re.S)
_re_con_sup = re.compile('\B!{([^<>\/].+?)}!\B', re.UNICODE|re.I|re.M|re.S)
_re_con_code = re.compile('\B{{{{([^<>\/].+?)}}}}\B', re.UNICODE|re.I|re.M|re.S)
def content_formate(text):
    #code
    #print _re_con_code.findall(text)
    #todo 边界处理问题
    if _re_con_code.search(text):
        text = _re_con_code.sub(r'<code>\1</code>', text)
    #h2 title
    if _re_title_h2.search(text):
        text = _re_title_h2.sub(r' <span id="h2_t">\1</span> ', text)
    #sup
    if _re_con_sup.search(text):
        text = _re_con_sup.sub(r'<div id="sup">\1</div>', text)
    #auto img
    if _re_imgs.search(text):
        text = _re_imgs.sub(r'<a class="imga" href="\1"><img class="lazy" border="0" style="max-width:540px;" src="http://mit00.02753.com/theones/static/grey2.gif" data-original="\1"/></a>', text)
    #mentions
    if '@' in text:
        text = _re_mentions.sub(r'<span id="sup"><a class="aherfa" href="/u/\1">@\1</a></span>', text)
    #youku
    if 'v.youku.com' in text:
        text = _re_youku.sub(r'<embed src="http://player.youku.com/player.php/sid/\1/v.swf" quality="high" width="540" height="380" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>', text)
    #tudou
    if 'www.tudou.com' in text:
        text = _re_tudou.sub(r'<embed src="http://www.tudou.com/v/\2/&resourceId=0_05_05_99&iid=152278332&bid=05/v.swf" quality="high" width="540" height="380" align="middle" allowScriptAccess="sameDomain" type="application/x-shockwave-flash"></embed>', text)
    #qq
    if 'v.qq.com' in text:
        text = _re_qq.sub(r'<embed src="http://static.video.qq.com/TPout.swf?vid=\2&auto=0" allowFullScreen="true" quality="high" width="540" height="380" align="middle" allowScriptAccess="always" type="application/x-shockwave-flash"></embed>', text)
    #gist
    if '://gist' in text:
        text = _re_gist.sub(r'<script src="\1.js"></script>',text)
    #url
    if 'http' in text:
        return autolink(text)
        #text = _re_urls.sub(r'<a href="\1" rel="nofollow" target="_blank">\1</a>', text)
    return text

# 格式时间,输出
def setdateo(otimes,otype):
    if not otype:
        otype = '1'
    if otype == '2':
        otimes = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(int(otimes)))
    elif otype == '3':
        otimes = time.strftime('%Y-%m',time.localtime(int(otimes)))
    elif otype == '4':
        otimes = time.strftime('%Y-%m-%d %H:%M',time.localtime(int(otimes)))
    elif otype == '5':
        otimes = time.strftime('%m-%d',time.localtime(int(otimes)))
    else:
        otimes = time.strftime('%Y-%m-%d',time.localtime(int(otimes)))
    return otimes

def nl2br(str):
    #s = escape(str)
    s = str.replace("\r\n", "<br>")
    return s

def clear2nbsp(str):
    s = escape(str)
    s = s.replace(" ", "")
    return s

def pickle_dumps(am):
    return pickle.dumps(am)

def pickle_loads(am):
    return pickle.loads(am)

# 缓存
def get_cache(key, value, timeout=60):
    cache_value = cache.get(key)
    if cache_value is None:
        cache_value = value
        cache.set(key,value,timeout=timeout)
    return cache_value

def read_cache(key):
    return cache.get(key)

# check user 等级
def checkuserflag(flag):
    if flag == '1':
        fname = 'normal'
    elif flag == '675':
        fname = 'admin'
    else:
        fname = 'clock'
    return fname