from xbmcswift2 import Plugin
from resources.lib.reddit import getRedditGfycats
import xbmcgui

plugin = Plugin()

def error(msg):
    xbmcgui.Dialog().notification('Error reading /r/soccer',msg, icon = xbmcgui.NOTIFICATION_ERROR,time=20000)
    plugin.log.error(msg)

@plugin.route('/')
def index():
    res = getRedditGfycats('soccer')
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
#        plugin.add_to_playlist(items,'video')
        return items
    
    else:
        if err.get('type') == 'http':
            error('HTTP ' + str(err.get('code')))
        else:
            error('Unknown')
        return
            
    

if __name__ == '__main__':
    plugin.run()
