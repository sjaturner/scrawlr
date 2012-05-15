import sys
import time
import pygame
import random
import simplejson
import pprint

ink=(0,0,0)
paper=(255, 255, 255)
maxint=sys.maxint
minint=-sys.maxint-1

record=[]
stroke=[]

orgx=0
orgy=0

def stroke_render(s):
    pointlist=[]
    if len(s)<2:
        return
    for item in s:
        x=item['pos'][0]-orgx
        y=item['pos'][1]-orgy
        pointlist.append((x,y))
    pygame.draw.lines(screen,ink,False,pointlist,1)

def render():
    screen.fill(paper)
    for item in record:
        stroke_render(item['stroke'])
    if stroke:
        stroke_render(stroke)
    pygame.display.flip()
    pass

def stroke_append(pos):
    event={}
    event['time']=time.time()
    x=pos[0]+orgx
    y=pos[1]+orgy
    event['pos']=(x,y)
    stroke.append(event)

def bbox(s):
    minx=maxint
    miny=maxint
    maxx=minint
    maxy=minint
    for item in s:
        x,y=item['pos']
        if x<minx:
            minx=x
        if y<miny:
            miny=y
        if x>maxx:
            maxx=x
        if y>maxy:
            maxy=y
    return ((minx,miny),(maxx,maxy))
    
def main():
    global stroke
    global orgx
    global orgy

    dorg=(0,0)
    drag=0
    down=0
    pygame.display.flip()

    while True:
        e=pygame.event.wait()
        if e.type == pygame.QUIT:
            return

        pressed=pygame.mouse.get_pressed()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button==2:
            drag=1
            dorg=e.pos
        elif e.type == pygame.MOUSEBUTTONUP and e.button==2:
            drag=0
        if e.type == pygame.MOUSEBUTTONDOWN and e.button==1:
            down=1
            stroke=[]
            stroke_append(e.pos)
        elif e.type == pygame.MOUSEBUTTONUP and e.button==1:
            down=0
            stroke_append(e.pos)
            record.append({'stroke':stroke,'bbox':bbox(stroke)})
        elif e.type == pygame.MOUSEMOTION:
            if drag:
                x=dorg[0]-e.pos[0]
                y=dorg[1]-e.pos[1]
                orgx+=x
                orgy+=y
                dorg=e.pos
            elif down:
                stroke_append(e.pos)
                
        render()

if len(sys.argv)==1:
    filename=str(int(time.time()))+'.paper'
else:
    for file in sys.argv:
        print file
    
screen=pygame.display.set_mode((800,600))
render()

main()

print orgx,orgy
print simplejson.dumps(record)
