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

def stroke_render(s):
    pointlist=[]
    if len(s)<2:
        return
    for item in s:
        pointlist.append(item['pos'])
    pygame.draw.lines(screen,ink,False,pointlist,1)

def render():
    screen.fill(paper)
    for s in record:
        stroke_render(s)
    if stroke:
        stroke_render(stroke)
    pygame.display.flip()
    pass

def stroke_append(pos):
    event={}
    event['time']=time.time()
    event['pos']=pos
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
    
def main():

    global stroke
    down=0
    pygame.display.flip()

    while True:
        e=pygame.event.wait()
        if e.type == pygame.QUIT:
            return

        pressed=pygame.mouse.get_pressed()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button==1:
            down=1
            stroke=[]
            stroke_append(e.pos)
        elif e.type == pygame.MOUSEBUTTONUP and e.button==1:
            down=0
            stroke_append(e.pos)
            record.append(stroke)
        elif e.type == pygame.MOUSEMOTION:
            if down:
                stroke_append(e.pos)
                
        render()

if len(sys.argv)==1:
    filename=str(int(time.time()))+'.paper'
else:
    for file in sys.argv:
        print file
    
screen=pygame.display.set_mode((800,600))
screen.fill(paper)

main()
