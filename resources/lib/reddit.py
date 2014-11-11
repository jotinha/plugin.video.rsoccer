# -*- coding: utf-8 -*-

import requests
import re

HEADERS = {'User-agent':'plugin.video.rsoccer'}


def getGfycatVideo(url,filetype='mp4'):
    if filetype not in ('mp4','webm','gif'):
        return
    m = re.match('^(https?:\/\/)?(wwww\.)?gfycat\.com\/([\w-]+)', url)
    if m and m.group(3):
        r = requests.get('http://gfycat.com/cajax/get/' + m.group(3), headers=HEADERS)
        if r.status_code == 200:
            d = r.json()['gfyItem']
            return d.get(filetype + 'Url'),d.get(filetype + 'Size')


def getRedditGfycats(subreddit,page='hot'):
    res = []
    r = requests.get('http://www.reddit.com/r/' + subreddit + '/' + page + '/.json',headers=HEADERS)
    
    if r.status_code == 200:
        for c in r.json()['data']['children']:
            cd = c['data']

            video_and_size = getGfycatVideo(cd['url'])
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
    
    return {'items':res}
