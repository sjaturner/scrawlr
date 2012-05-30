#   in this order
#       ensure that the angle and points representations overlay correctly with distance along stroke equivalence (done)
#       be able to slice stuff up using the median filter corner detection trick (done)
#       build a library of the split stuff which references back to the original strokes (done)
#       consider inserting paired stuff into library in case the split has been over zealous
#       the library will contain downsampled sliced stuff with say sixteen sample points median filtered (done)
#       some way of displaying this on the fly would be nice (done)
#       consider crossing detection as another cue
#       colours for inferred characters, told characters and unknown characters

import os
import sys
import time
import pygame
import random
import simplejson
import pprint
import numpy

width=1200
height=600
ink=(0,0,0)
paper=(255, 255, 255)
red=(255, 0, 0)
line=(255-0x40, 255-0x40, 255-0x40)
maxint=sys.maxint
minint=-sys.maxint-1

selected_item=None
do_letters=None
record=[]
stroke=[]
sel=None
sel_w=0
sel_h=0

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

sections={}
last_section={}

def section_render(section,x,y,colour):
    pygame.draw.rect(screen,ink,((x,y),(32,int(4*numpy.pi))),1)
    off=0
    for val in section:
        lx=int(x+off*2)
        ly=int(y+2*(val%(2*numpy.pi)))
        pygame.draw.circle(screen,colour,(lx,ly),1,0)
        off+=1


def show_correlation():
    x=0
    y=8
    for section in sections:
        section_render(section,x,y,ink)
        for correlated in sections[section]['best']:
            x+=40
            score=8*correlated['score']
            if score>255:
                score=255
            resampled=correlated['resampled']
            if correlated==last_section: # does not work yet
                gb=0
            else:
                gb=score
            colour=(score,gb,gb)
            section_render(resampled,x,y,colour)
        y+=20
        x=0
    
def is_inside(outer,inner):
    (outer_lt_x,outer_tl_y)=outer[0]
    (outer_br_x,outer_br_y)=outer[1]

    (inner_lt_x,inner_tl_y)=inner[0]
    (inner_br_x,inner_br_y)=inner[1]

    return outer_lt_x<inner_lt_x and outer_tl_y<inner_tl_y and outer_br_x>inner_br_x and outer_br_y>inner_br_y

def find_stroke(bbox):
    for item in record:
        if is_inside(bbox,item['bbox']):
            return item
    return None
    
def render_char(x,y,c,colour):
    text = font.render('%c'%c,0,colour)
    textrect = text.get_rect()
    textrect.centerx=x
    textrect.centery=y
    pygame.draw.rect(screen,paper,textrect)
    screen.blit(text,textrect)

def render():
    global font
    linegap=40
    colgap=width
    screen.fill(paper)


#   show_correlation()

    for y in range(0,height,linegap):
        oy=y-orgy%linegap
        pygame.draw.lines(screen,line,False,((0,oy),(width,oy)),1)
    for item in record:
        if 'colour' in item:
            colour=item['colour']
        else:
            colour=ink
        stroke_render(item['stroke'],colour)
        if do_letters and 'bbox' in item and 'char' in item:
            bbox=item['bbox']
            if item['char']['type']=='told':
                col=(255,0,0)
            else:
                col=ink
            render_char(bbox[0][0],bbox[0][1],item['char']['val'],col)

    if stroke:
        stroke_render(stroke,ink)

    if sel and sel_w and sel_h:
        pygame.draw.rect(screen,(255,0,0),((sel[0],sel[1]),(sel_w,sel_h)),1)
     
    pygame.display.flip()

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

def add_section(data,sec):
    #   for now, need to add the new section and recalculate the best fits
    #   which will get tiring pretty soon
    #   also need a way to display this stuff
    #       maybe just render it on the page each time 
    sections[sec['resampled']]={'len':sec['len'],'data':data}

    for outer in sections:
        scores={}
        for inner in sections:
            if outer==inner:
                continue
            scores[correlate(outer,inner)]=inner
        sections[outer]['best']=[{'score':score,'resampled':scores[score]} for score in sorted(scores.keys())]
    last_section=sec['resampled']

#   pprint.pprint(sections)

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
#   record.append(sparkline_angle(data))
    sparkline_filter(data)

    mat=[]
    for (i,sec) in enumerate(data['sec']):
#       print i,sec
        thing=sections[sec['resampled']]['best']
        if len(thing):
            if 'data' in sections[thing[0]['resampled']]:
                pprint.pprint(sections[thing[0]['resampled']]['data'])
                if 'char' in sections[thing[0]['resampled']]['data']:
                    print sections[thing[0]['resampled']]['data']['char']
                    if 'sec' in sections[thing[0]['resampled']]['data']:
                        for (j,h) in enumerate(sections[thing[0]['resampled']]['data']['sec']):
#                           print thing[0]['resampled']
#                           print h['resampled'] 
#                           print

                            if thing[0]['resampled']==h['resampled']:
                                mat.append((i,j,sections[thing[0]['resampled']]['data']['char']))

    print mat

    #   here is where we try to guess the letter
    #       for each resampled section
    #           find best correlated resampled
    #           find out if this is part of a tagged section 
    #           is it the corresponding part
    #
    #   need soon to consider letters made of more than one element, 't' is an example of this

def main():
    global stroke
    global orgx
    global orgy
    global sel
    global sel_w
    global sel_h
    global selected_item
    global do_letters

    dorg=(0,0)
    drag=0
    down=0
    pygame.display.flip()

    while True:
        refresh=1
        e=pygame.event.wait()
        if e.type == pygame.QUIT:
            return

        pressed=pygame.mouse.get_pressed()

        if e.type == pygame.KEYDOWN:
            if e.unicode and selected_item:
                selected_item['char']={'val':e.unicode,'type':'told'}
        elif e.type == pygame.KEYUP:
            sel=None
            sel_w=0
            sel_h=0

        if e.type == pygame.MOUSEBUTTONDOWN and e.button==3:
            sel=e.pos
            do_letters=1
            sel_w=0
            sel_h=0
        elif e.type == pygame.MOUSEBUTTONUP and e.button==3:
            selected_item=find_stroke(((sel[0],sel[1]),(e.pos[0],e.pos[1])))

            do_letters=0
#           if selected_item:
#               pprint.pprint(selected_item)
            
            sel_w=e.pos[0]-sel[0]
            sel_h=e.pos[1]-sel[1]

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
                refresh=0
                stroke_append(e.pos)
                stroke_render(stroke,ink)
                pygame.display.update()
                
        if refresh:
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
pygame.font.init()
font=pygame.font.Font(None, 20)
render()

main()

print simplejson.dumps(record)
print orgx,orgy
