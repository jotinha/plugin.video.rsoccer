from xbmcswift2 import Plugin
from resources.lib.reddit import getRedditVideos
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
            item = {
                'label': '%(title)s (%(ups)s)' % r,
                'path': r.get('video'),
                'is_playable': True
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
