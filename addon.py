from xbmcswift2 import Plugin
from resources.lib.reddit import getRedditVideos
from resources.lib.common import GET
import datetime
try:
    import xbmcgui
except ImportError:
    from xbmcswift2 import xbmc, xbmcgui

plugin = Plugin()

def error(msg):
    xbmcgui.Dialog().notification('Error reading /r/soccer',msg, icon = xbmcgui.NOTIFICATION_ERROR,time=20000)
    plugin.log.error(msg)

@plugin.route('/')
def index():
    res = getRedditVideos('soccer',after = plugin.request.args.get('after'), before = plugin.request.args.get('before'))
    err = res.get('error')
    
    if not err:
        items = []    

        for r in res.get('items') or []:
            
            date = r.get('date')
            if date:
                date = datetime.datetime.fromtimestamp(date)
                r['date_in_plot'] = date.strftime('%Y/%m/%d, %H:%M')
               
            item = {
                'label': '%(title)s (%(ups)s)' % r,
                'path': r.get('video'),
                'thumbnail': r.get('thumbnail'),
                'is_playable': True,
                'info': {
                    'title': r.get('title'),
                    'artist': [r.get('author')],
                    'plot': '%(title)s\nPosted by u/%(author)s on %(date_in_plot)s\n%(ups)s upvotes' % r,
                    'date': date.strftime('%d.%m.%Y'), # must be this format
                    'size': r.get('size'), #size, in bytes
                },
                'info_type': 'video',
            }
           
            items.append(item)
            
        if res.get('next'):
            items.append({
                    'label': 'Next >>',
                    'path': plugin.url_for('index',after=res.get('next'))
                })
                
        return items
    
    else:
        if err.get('type') == 'http':
            error('HTTP ' + str(err.get('code')))
        else:
            error('Unknown')
        return
            
if __name__ == '__main__':
    plugin.run()
