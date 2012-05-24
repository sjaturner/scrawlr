#   in this order
#       ensure that the angle and points representations overlay correctly with distance along stroke equivalence (done)
#       be able to slice stuff up using the median filter corner detection trick (done)
#       build a library of the split stuff which references back to the original strokes
#       consider inserting paired stuff into library in case the split has been over zealous
#       the library will contain downsampled sliced stuff with say sixteen sample points median filtered
#       some way of displaying this on the fly would be nice
#       consider crossing detection as another cue

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

                ret.append((int(acc_x),angle))
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

def correlate(a,b):
    if len(a)!=len(b):
        print 'correlate only works for matched length sections'
        sys.exit

    return sum(map(lambda (x,y):abs(poldiff(x,y)),zip(a,b)))

sections={}
def add_section(data,sec):
    #   for now, need to add the new section and recalculate the best fits
    #   which will get tiring pretty soon
    #   also need a way to display this stuff
    #       maybe just render it on the page each time 
    sections[sec['resampled']]={'len':sec['len']} # ,'data':data}

    for outer in sections:
        scores={}
        for inner in sections:
            if outer==inner:
                continue
            scores[correlate(outer,inner)]=inner
        sections[outer]['best']=[{'score':score,'resampled':scores[score]} for score in sorted(scores.keys())]

    pprint.pprint(sections)

def resample(a,n):
    while len(a)<64:
        a=[val for val in a for x in (0, 1)]

    step=float(len(a))/float(n)
    base=0.0
    ret=[]
    while base<len(a):
        slice=a[int(base):int(base+step)]
        base+=step;
        slice.sort()
        ret.append(med(slice)) 
    return tuple(ret)

def sparkline_filter(data):
    ret={}
    ret['stroke']=[]

    graph=distangle(data['stroke'])
    points={}

    minx=maxint
    maxx=minint

#   for x,y in graph:
#       print x,y
#   print

    scale=100.0
    if len(graph)<2:
        return

    for i in range(0,len(graph)-1):
        x0=int(graph[i+0][0])
        y0=int(scale*graph[i+0][1])
        x1=int(graph[i+1][0])
        y1=int(scale*graph[i+1][1])
        for (x,y) in line_points(x0,y0,x1,y1):
            ix=int(x)
            if ix>maxx:
                maxx=ix
            if ix<minx:
                minx=ix
            if ix in points:
                points[ix].append(y/scale)
            else:
                points[ix]=[y/scale]

    uniq_points=[]

    last=mean(points[minx])
    for x in range(minx,maxx+1):
        if x in points:
            m=mean(points[x])
            uniq_points.append([x,m])
            last=m
        else:
            uniq_points.append([x,last])

#   for p in uniq_points:
#       print p

    gap=7

    if len(uniq_points)>2*gap:
        for i in range(gap):
            uniq_points[i].append(0)
        for i in range(gap,len(uniq_points)-gap):
            uniq_points[i].append(abs(poldiff(uniq_points[i-gap][1],uniq_points[i+gap][1])))
        for i in range(len(uniq_points)-gap,len(uniq_points)):
            uniq_points[i].append(0)
        arg=[int(x[2]*1000) for x in uniq_points]
        median=bucket(arg,(2*gap)/gap+1,med)

    threshold=2.0
    ret=map(lambda x:[x[0][0],x[0][1],x[0][2],x[1]/1000.0,(0,1)[x[1]/1000.0<2.0]],zip(uniq_points,median))
#   for item in ret:
#       print item[0],item[1],item[2],item[3],item[4]

    nsample=16

    state='up'
    tot=[]
    sec=[]

    acc=[]
    for x,y,a,m,t in ret:
        tot.append(y)
        if state=='up' and not t:
            sec.append({'len':len(acc),'resampled':resample(acc,nsample)})
            state='down'
        elif state=='down' and t:
            acc=[]
            state='up'
        if state=='up':
            acc.append(y)
    if acc:
        sec.append({'len':len(acc),'resampled':resample(acc,nsample)})

    data['sec']=sec
    data['tot']=tot

    for section in sec:
        add_section(data,section)

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
