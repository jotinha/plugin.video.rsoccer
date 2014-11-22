# -*- coding: utf-8 -*-
"""
Created on Sat Nov 22 16:45:51 2014

@author: jsousa
"""

import requests

HEADERS = {'User-agent':'plugin.video.rsoccer'}

def sget(item,key):
    keys = key.split('/')
    try:
        for k in keys:
            if item and k:
                item = item[k]
        return item
    except KeyError:
        return None

def GET(url,**kwargs):
    kwargs.setdefault('headers',HEADERS)
    return requests.get(url,**kwargs)

def html_unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace('&quot;','"')
    s = s.replace('&apos;',"'")
    # this has to be last:
    s = s.replace("&amp;", "&")
    return s 
    
