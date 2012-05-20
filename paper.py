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
red=(255, 0, 0)
line=(255-0x40, 255-0x40, 255-0x40)
maxint=sys.maxint
minint=-sys.maxint-1

record=[]
stroke=[]

orgx=0
orgy=0

start_time=time.time()
start_tick=pygame.time.get_ticks()

def line_points(x0, y0, x1, y1):
   sx=x0
   sy=y0
   a=[]
   steep = abs(y1 - y0) > abs(x1 - x0)
   if steep:
      x0, y0 = y0, x0  
      x1, y1 = y1, x1

   if x0 > x1:
      x0, x1 = x1, x0
      y0, y1 = y1, y0
   
   if y0 < y1: 
      ystep = 1
   else:
      ystep = -1

   deltax = x1 - x0
   deltay = abs(y1 - y0)
   error = -deltax / 2
   y = y0

   for x in range(x0, x1 + 1): # We add 1 to x1 so that the range includes x1
      if steep:
         a.append((y, x))
      else:
         a.append((x, y))
            
      error = error + deltay
      if error > 0:
         y = y + ystep
         error = error - deltax
   
   (x,y)=a[0]
   if x==sx and y==sy:
      pass
   else:
      a.reverse()

   return a

def med(a):
    return sorted(a)[len(a)/2]

def bucket(samples,gap,fun):
    if not gap%2:
        sys.exit()
    extended=[samples[0]]*(gap/2)+samples+[samples[-1]]*(gap/2)
    ret=[]
    for i in range(0,len(samples)):
        ret.append(fun(extended[(i):(i+gap)]))
    return ret
   
def paper_time():
    return time.time()
    return start_time+(start_tick-pygame.time.get_ticks())/1000.0
    
def stroke_render(s,colour):
    pointlist=[]
    if len(s)<2:
        return
    for item in s:
        x=item['pos'][0]-orgx
        y=item['pos'][1]-orgy
        pointlist.append((x,y))
    pygame.draw.lines(screen,colour,False,pointlist,1)

def render():
    linegap=40
    colgap=width
    screen.fill(paper)
    for y in range(0,height,linegap):
        oy=y-orgy%linegap
        pygame.draw.lines(screen,line,False,((0,oy),(width,oy)),1)
    for item in record:
        if 'colour' in item:
            colour=item['colour']
        else:
            colour=ink
        stroke_render(item['stroke'],colour)
    if stroke:
        stroke_render(stroke,ink)
    pygame.display.flip()
    pass

def stroke_append(pos):
    event={}
    event['time']=paper_time()
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
    
def distangle(stroke):
    first=1
    fangle=1
    acc_x=0
    ret=[]
    for event in stroke:
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
                acc_x+=r
                t=numpy.arctan2(dy, dx)
                if fangle:
                    fangle=0
                    angle=t
                    old_t=t
                else:
                    delta_t=t-old_t
                    if delta_t<numpy.pi:
                        delta_t+=2*numpy.pi
                    if delta_t>numpy.pi:
                        delta_t-=2*numpy.pi
                    angle+=delta_t

                ret.append((acc_x,angle))
                old_t=t
        old_x=x
        old_y=y
    return ret

def sparkline_angle(data):
    ret={}
    ret['stroke']=[]
    base_x=data['bbox'][1][0]
    base_y=(data['bbox'][0][1]+data['bbox'][1][1])/2

    graph=distangle(data['stroke'])

    for (x,y) in graph:
        ret['stroke'].append({'pos':(base_x+x,base_y+y*10),'time':0})
        
    ret['bbox']=bbox(ret['stroke'])
    ret['colour']=red
    return ret

def mean(a):
    return sum(a)/len(a)

def poldiff(a,b):
    pi=numpy.pi
    ret=a-b
    while ret<-pi:
        ret+=2*pi
    while ret>+pi:
        ret-=2*pi
#   print  '   ',a,b,ret
    return ret

def filter(a,swing,bw,bs):
    ret=[]
    if len(a)<2*bw+1:
        return ret
    for center in range(0+bw,len(a)-bw):
        best_score=0
        best_scan=0.0
        scan=0.0
        while scan<2*numpy.pi:
            score=0
#           print scan
            for i in range(center-bw,center):
                y=a[i][1]
                if abs(poldiff(y,scan-swing))<numpy.pi/(2*bs):
                    score+=1
#                   print '      score',numpy.pi/(2*bs)
            for i in range(center,center+bw):
                y=a[i][1]
                if abs(poldiff(y,scan+swing))<numpy.pi/(2*bs):
                    score+=1
#                   print '      score',numpy.pi/(2*bs)
            if score>best_score:
                best_score=score
                best_scan=scan
            scan+=numpy.pi/(4*bs)
        ret.append((best_scan,best_score))
        print center,best_scan,best_score
    return ret


def sparkline_filter(data):
    ret={}
    ret['stroke']=[]
    base_x=data['bbox'][1][0]
    base_y=(data['bbox'][0][1]+data['bbox'][1][1])/2

    graph=distangle(data['stroke'])
    points={}

    minx=maxint
    maxx=minint

    if len(graph)>=2:
        for i in range(0,len(graph)-1):
            x0=graph[i+0][0]
            y0=graph[i+0][1]
            x1=graph[i+1][0]
            y1=graph[i+1][1]
            for (x,y) in line_points(x0,y0,x1,y1):
                ix=int(x)
                if ix>maxx:
                    maxx=ix
                if ix<minx:
                    minx=ix
                if ix in points:
                    points[ix].append(y)
                else:
                    points[ix]=[y]

    uniq_points=[]
    
    last=mean(points[minx])
    for x in range(minx,maxx+1):
        if x in points:
            m=mean(points[x])
            uniq_points.append((x,m))
            last=m
        else:
            uniq_points.append((x,last))

    filter(uniq_points,numpy.pi/2,10,8)
    
def record_append(data):
    record.append(data)
    record.append(sparkline_angle(data))
    sparkline_filter(data)

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
