import os
import sys
import time
import pygame
import random
import simplejson
import pprint
import numpy

width=800
height=600
ink=(0,0,0)
paper=(255, 255, 255)
line=(255-0x40, 255-0x40, 255-0x40)
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
    linegap=40
    colgap=width
    screen.fill(paper)
    for y in range(0,height,linegap):
        oy=y-orgy%linegap
        pygame.draw.lines(screen,line,False,((0,oy),(width,oy)),1)
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
    
def sparkline_angle(data):
    ret={}
    ret['stroke']=[]
    first=1
    base_x=data['bbox'][1][0]
    acc_x=base_x
    base_y=(data['bbox'][0][1]+data['bbox'][1][1])/2
    for event in data['stroke']:
        pos=event['pos']
        x=pos[0]
        y=pos[1]
        if first:
            first=0
        else:
            dx=x-old_x
            dy=y-old_y
            r=numpy.sqrt(dx**2 + dy**2)
            if r>0.0:
                t=numpy.arctan2(dy, dx)
                acc_x+=r
                ret['stroke'].append({'pos':(acc_x,base_y+t*10),'time':time.time()})
        old_x=x
        old_y=y
    ret['bbox']=bbox(ret['stroke'])
    return ret
    
def record_append(data):
    record.append(data)
    record.append(sparkline_angle(data))

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
            record_append({'stroke':stroke,'bbox':bbox(stroke)})
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

if len(sys.argv)==2:
    filename=sys.argv[1]
    if os.path.exists(filename):
        f=open(filename)
        json=f.readline()
        record=simplejson.loads(json)
        org=f.readline().strip().split()
        orgx=int(org[0])
        orgy=int(org[1])
    
screen=pygame.display.set_mode((width,height))
render()

main()

print simplejson.dumps(record)
print orgx,orgy
