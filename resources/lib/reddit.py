# -*- coding: utf-8 -*-

import requests
import re

HEADERS = {'User-agent':'plugin.video.rsoccer'}


def getVideoGfycat(item,filetype='mp4'):
    if filetype not in ('mp4','webm','gif'):
        return
    url = item.get('url')
    m = re.match('^(https?:\/\/)?(wwww\.)?gfycat\.com\/([\w-]+)', url)
    if m and m.group(3):
        r = requests.get('http://gfycat.com/cajax/get/' + m.group(3), headers=HEADERS)
        if r.status_code == 200:
            d = r.json()['gfyItem']
            return d.get(filetype + 'Url'),d.get(filetype + 'Size')

def getVideoYoutube(item):
    def url2plugin(url):
        video_id = re.search('[?&]v=([\-\w]+)', url)
        if video_id and video_id.group(1):
            return 'plugin://plugin.video.youtube/?action=play_video&videoid=' + video_id.group(1)
    
    url = item.get('url')
    if url:
        return url2plugin(url),None

def getVideo(item):
    media = item.get('secure_media') or item.get('media')
    domain = item.get('domain')
    if (media and media.get('type') == 'youtube.com') or domain == 'youtube.com':
        return getVideoYoutube(item)
    
    elif domain == 'gfycat.com':
        return getVideoGfycat(item)

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
            
            video_and_size = getVideo(cd)
            if video_and_size:
               
                res.append({
                    'title': cd['title'],
                    'author': cd['author'],
                    'ups' : cd['ups'],
                    'video': video_and_size[0],
                    'size': video_and_size[1],
                    'date': cd['created_utc']
                    
                })                
                
#                print '%(title)s - %(author)s (%(ups)s) - %(video)s' % res[-1]
    else:
        return {'error': {'type':'http','code':r.status_code}}
    
    return {'items':res,'next': data['after']}
