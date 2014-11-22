# -*- coding: utf-8 -*-

import requests
from requests.utils import unquote
import re

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
            return url

def getVideoGfycat(item,filetype='mp4'):
    if filetype not in ('mp4','webm','gif'):
        return
    url = item.get('url')
    m = re.match('^(https?:\/\/)?(wwww\.)?gfycat\.com\/([\w-]+)', url)
    if m and m.group(3):
        r = requests.get('http://gfycat.com/cajax/get/' + m.group(3), headers=HEADERS)
        if r.status_code == 200:
            d = r.json()['gfyItem']
            return d.get(filetype + 'Url')#,d.get(filetype + 'Size')

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
        return url2plugin(url)

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
        'limit': 100,
        'after': after,
        'before': before,
    }
    r = requests.get('http://www.reddit.com/r/' + subreddit + '/' + page + '/.json',params=params,headers=HEADERS)
    
    if r.status_code == 200:
        data = r.json()['data']
        for c in data['children']:
            
            cd = c['data']
            
            vid = getVideo(cd)
            if vid != 'novideo':
                if vid:
                    res.append({
                        'title': cd['title'],
                        'author': cd['author'],
                        'ups' : cd['ups'],
                        'video': vid,
                        'date': cd['created_utc']
                        
                    })                
                else:
                    print "ERROR: failed to parse video item"
                    display(cd)
                
#                print '%(title)s - %(author)s (%(ups)s) - %(video)s' % res[-1]
    else:
        return {'error': {'type':'http','code':r.status_code}}
    
    return {'items':res,'next': data['after']}
