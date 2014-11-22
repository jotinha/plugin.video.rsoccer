# -*- coding: utf-8 -*-

import requests
from requests.utils import unquote
import re
try:
    from .common import *
except ValueError:
    from common import *

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
    m = re.match('^(https?:\/\/)?(wwww\.)?gfycat\.com\/([\w-]+)', url)
    gfyid = m and m.group(3)
    if gfyid:
        r = GET('http://gfycat.com/cajax/get/' + gfyid)
        url = r.status_code == 200 and r.json()['gfyItem'].get(filetype + 'Url')
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
        return 'novideo',None
    

def getRedditVideos(subreddit,page='hot',after=None,before=None):
    res = []
    params = {
        'limit': 30,
        'after': after,
        'before': before,
    }
    r = GET('http://www.reddit.com/r/' + subreddit + '/' + page + '/.json',params=params)
    
    if r.status_code == 200:
        data = r.json()['data']
        for c in data['children']:
            
            cd = c['data']
            
            vid,more = getVideo(cd)
            if vid != 'novideo':
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
                    
                    res.append(item)
                
                else:
                    print "ERROR: failed to parse video item"
                    print cd
                
    else:
        return {'error': {'type':'http','code':r.status_code}}
    
    return {'items':res,'next': data['after']}

#r = getRedditVideos('soccer')