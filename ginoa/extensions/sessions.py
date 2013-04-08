#!/usr/bin/env python
#coding=utf-8
"""
    extensions.session
    ~~~~~~~~
    :origin version in https://gist.github.com/1735032
"""
try:
    import cPickle as pickle
except ImportError:
    import pickle


class Session(object):
    def __init__(self, get_secure_cookie, set_secure_cookie, name='_session', expires_days=None):
        self.set_session = set_secure_cookie
        self.get_session = get_secure_cookie
        self.name = name
        self._expiry = expires_days
        self._dirty = False
        self.get_data()
    
    def get_data(self):
        value = self.get_session(self.name)
        self._data = pickle.loads(value) if value else {}

    def set_expires(self, days):
        self._expiry = days

    def __getitem__(self, key):
        return self._data[key]
    
    def __setitem__(self, key, value):
        self._data[key] = value
        self._dirty = True
    
    def __delitem__(self, key):
        if key in self._data:
            del self._data[key]
            self._dirty = True
        
    def __contains__(self, key):
        return key in self._data
    
    def __len__(self):
        return len(self._data)
    
    def __iter__(self):
        for key in self._data:
            yield key
    
    def __del__(self):
        self.save()

    def save(self):
        if self._dirty:
            self.set_session(self.name, pickle.dumps(self._data), expires_days=self._expiry,httponly=True)
            self._dirty = False


