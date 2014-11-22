# -*- coding: utf-8 -*-

import requests
from requests.utils import unquote
import re
try:
    from .common import *
except ValueError:
    from common import *

DEBUG = False
if DEBUG:
    import os,json

def getVideoVine(item):
    #first attempt to get mp4 directly from embed content
    iframe = sget(item,'secure_media/oembed/html') or \
             sget(item,'media/oembed/html') or \
             sget(item,'secure_media_embed/content') or \
             sget(item,'media_embed/content')

    if iframe:
        m = re.search('[?&]src=(https?.*?vine\.co.*?)&amp;',iframe)
        if m and m.group(1):
            url = unquote(m.group(1))
            return url,None

def getVideoGfycat(item,filetype='mp4'):
    if filetype not in ('mp4','webm','gif'):
        return
    url = item.get('url')
    m = re.match('^(https?:\/\/)?(www\.)?gfycat\.com\/([\-\w]+)', url)
    gfyid = m and m.group(3)
    if gfyid:
        if not DEBUG:
            r = GET('http://gfycat.com/cajax/get/' + gfyid)
            url = r.status_code == 200 and r.json()['gfyItem'].get(filetype + 'Url')
        else:
            url = 'file://debug_disabled'
        thumbnail = 'https://thumbs.gfycat.com/' + gfyid + '-thumb100.jpg'
        return url, {'thumbnail':thumbnail}

def getVideoYoutube(item):
    def getVideoId(url):
        for rexp in ['[?&]v=([\-\w]+)', '/embed/([\-\w]+)','^https?:\/\/youtu\.be\/([\-\w]+)']:
            video_id = re.search(rexp,url)
            if video_id and video_id.group(1):
                return video_id.group(1)
        
    def url2plugin(url):
        video_id = getVideoId(url)
        if video_id:
            return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + video_id
    
    url = item.get('url')   

    if url:
        return url2plugin(url), None


def getEmbedThumbnail(item):
    thumbnail = sget(item,'secure_media/oembed/thumbnail_url') or \
                sget(item,'media/oembed/thumbnail_url')
    
    if thumbnail:
        return html_unescape(thumbnail)

def getVideo(item):
    media = item.get('secure_media') or item.get('media')
    domain = item.get('domain')
    if domain == 'youtube.com' or domain == 'youtu.be':
        return getVideoYoutube(item)
    
    elif domain == 'gfycat.com':
        return getVideoGfycat(item)

    elif domain == 'vine.co':
        return getVideoVine(item)
    
    else:
        return 'novideo'
    

def getRedditVideos(subreddit,page='hot',after=None,before=None):
    res = []
    params = {
        'limit': 30,
        'after': after,
        'before': before,
    }
    

    if not DEBUG:
        r = GET('http://www.reddit.com/r/' + subreddit + '/' + page + '/.json',params=params)
        data = r.status_code == 200 and r.json()['data']
    else:
        data = json.load(open(os.path.expanduser('~/debug.json'),'rt'))['data']
    
    
    if data:
        for c in data['children']:
            
            cd = c['data']
            
            vid_and_more = getVideo(cd)
            if vid_and_more != 'novideo':
                try:
                    vid,more = vid_and_more
                except TypeError:
                    print "ERROR: failed to parse", cd
                if vid:
                    item = {
                            'title': cd['title'],
                            'author': cd['author'],
                            'ups' : cd['ups'],
                            'date': cd['created_utc'],
                            'video': vid,
                        }
                    if more:
                        item.update(more)
                    
                    if not item.get('thumbnail'):
                        thumbnail = getEmbedThumbnail(cd)
                        if thumbnail:
                            item['thumbnail'] = thumbnail
                        
                    if DEBUG:
                        del item['thumbnail']
                    
                    res.append(item)
                
                else:
                    print "ERROR: failed to parse video item"
                    print cd
                
    else:
        return {'error': {'type':'http','code':r.status_code}}
    
    return {'items':res,'next': data['after']}

r = getRedditVideos('soccer')