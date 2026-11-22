import cairo
from ink import *; from chars import *; from props import bottle
s=cairo.ImageSurface(cairo.FORMAT_ARGB32,W,H); c=cairo.Context(s)
c.set_source_surface(paper_surface(),0,0); c.paint()
text(c,'NOUVEAU PRÉSENTATEUR',540,90,80,fill=YEL if False else hexc('#ffd23f'))
draw_char(c,'david',290,420,0.95,1.0,mouth=0.0,smile=0.6,eyes='open',arms=('down','point_side'))
draw_char(c,'david',790,420,0.95,1.3,mouth=0.7,eyes='wide',brows=1,arms=('face','face'))
def bot(cc,x,y,t): bottle(cc,x,y-40,0.5,t)
draw_char(c,'david',290,1250,0.95,1.6,mouth=0.35,smile=0.9,eyes='wink',arms=('down','hold_high'),prop=bot,prop_hand='R')
draw_char(c,'david',790,1250,0.95,1.9,outfit='chic',mouth=0,smile=0.9,eyes='closed',blush=1,arms=('down','down'))
for x,y,l in ((290,1020,'neutre'),(790,1020,'choqué'),(290,1850,'présente'),(790,1850,'tenue soirée')):
    text(c,l,x,y,54,font='Patrick Hand',fill=(1,1,1))
s.write_to_png('frames/planche_david.png')
