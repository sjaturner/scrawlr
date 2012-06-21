#   in this order
#       ensure that the angle and points representations overlay correctly with distance along stroke equivalence (done)
#       be able to slice stuff up using the median filter corner detection trick (done)
#       build a library of the split stuff which references back to the original strokes (done)
#       the library will contain downsampled sliced stuff with say sixteen sample points median filtered (done)
#       some way of displaying this on the fly would be nice (done)
#       colours for inferred characters, told characters and unknown characters(done)
#       consider inserting paired stuff into library in case the split has been over zealous
#       consider crossing detection as another cue
#       need to detect strokes which cross, use the bbox and then line algorithm

#   groups of connected strokes
#   letters are groups of connected strokes but some groups have only one member
#   as stroke, letter has a bounding box
#   going to need a list of letters somewhere
#   letter identity with stroke is simply incorrect

#   consider that intersecting regions may be for any stroke
#       numerous
#       prolonged
#   starts to look like a matrix representing a graph and these are hard to compare
#   expect that consideration of close matches and matrices will be required in some cases
#   however, many matches come out of the simple case of two or three strokes
#       most of the lower case set [fkx]
#       more complex upper case [abdfhikrx]
#   perhaps a simpler classification mechanism will suffice in the first instance
#       match the stroke components 
#       determine whether they are in contact with other related components
#       ignore the geometry and connectedness initially

#   think that selected item has to go though
#   require a table of connected strokes
#   entries to this in record append, at the end of this in fact

import os
import sys
import time
import pygame
import random
import simplejson
import pprint
import numpy
import itertools

width=1200
height=600
ink=(0,0,0)
paper=(255, 255, 255)
red=(255, 0, 0)
line=(255-0x40, 255-0x40, 255-0x40)
maxint=sys.maxint
minint=-sys.maxint-1

do_letters=None # renders letters too
letters=[]
strokes=[] # record of strokes with normalised angles and so on
current_stroke=[] # the one being built

# way to complicated
selected_letter=None # this ought to be the current selection bounding box
sel=None
sel_w=0
sel_h=0

# top left corner of rendered view
orgx=0
orgy=0

start_time=time.time()

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
    
def stroke_render(s,colour):
    pointlist=[]
    if len(s)<2:
        return
    for item in s:
        x=item['pos'][0]-orgx
        y=item['pos'][1]-orgy
        pointlist.append((x,y))
    pygame.draw.lines(screen,colour,False,pointlist,1)

last_data=None # just used to show the normalised angle data for the most recent stroke

def section_render(section,x,y,colour):
    pygame.draw.rect(screen,ink,((x,y),(32,int(4*numpy.pi))),1)
    off=0
    for val in section:
        lx=int(x+off*2)
        ly=int(y+2*(val%(2*numpy.pi)))
        pygame.draw.circle(screen,colour,(lx,ly),1,0)
        off+=1

def is_inside(outer,inner):
    (outer_tl_x,outer_tl_y)=outer[0]
    (outer_br_x,outer_br_y)=outer[1]

    (inner_tl_x,inner_tl_y)=inner[0]
    (inner_br_x,inner_br_y)=inner[1]

    return outer_tl_x<inner_tl_x and outer_tl_y<inner_tl_y and outer_br_x>inner_br_x and outer_br_y>inner_br_y

def point_in_bbox(point,bbox):
    (point_x,point_y)=point
    (bbox_tl_x,bbox_tl_y)=bbox[0]
    (bbox_br_x,bbox_br_y)=bbox[1]

    if point_x<bbox_tl_x or point_x>bbox_br_x:
        return False
    elif point_y<bbox_tl_y or point_y>bbox_br_y:
        return False
    else:
        return True

def bbox_overlap(a,b):
    (a_tl_x,a_tl_y)=a[0]
    (a_br_x,a_br_y)=a[1]
    
    (b_tl_x,b_tl_y)=b[0]
    (b_br_x,b_br_y)=b[1]

    if a_tl_x>b_br_x or a_br_x<b_tl_x or a_tl_y>b_br_y or a_br_y<b_tl_y:
        return False
    else:
        return True

def find_letter(bbox): # becomes some sort of iterator perhaps
    for letter in letters:
        for item in letter['item']:
            if is_inside(bbox,item['bbox']):
                return letter
    return None
    
def render_char(x,y,c,colour): # renders the characters near the letter
    x-=orgx
    y-=orgy
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

    if last_data:
        ix=0
        for sec in last_data['sec']:
            section_render(sec['resampled'],ix,0,0x80)
            ix+=34

    for y in range(0,height,linegap):
        oy=y-orgy%linegap
        pygame.draw.lines(screen,line,False,((0,oy),(width,oy)),1)

    for item in strokes:
        if 'colour' in item:
            colour=item['colour']
        else:
            colour=ink
        stroke_render(item['stroke'],colour)

    for letter in letters:
        item=letter['item'][0]
        if do_letters and 'bbox' in item and 'char' in letter:
            bbox=item['bbox']
            if letter['char']['type']=='told':
                col=(255,0,0)
            elif letter['char']['type']=='guess':
                col=(0,255,0)
            else:
                col=ink
            render_char(bbox[0][0],bbox[0][1],letter['char']['val'],col)

    if current_stroke:
        stroke_render(current_stroke,ink)

    if sel and sel_w and sel_h:
        pygame.draw.rect(screen,(255,0,0),((sel[0],sel[1]),(sel_w,sel_h)),1)
     
    pygame.display.flip()

def current_stroke_append(pos):
    event={}
    event['time']=paper_time()
    x=pos[0]+orgx
    y=pos[1]+orgy
    event['pos']=(x,y)
    current_stroke.append(event)

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

correlated={}

def correlate(a,b): # memoize this
    if len(a)!=len(b):
        print 'correlate only works for matched length sections'
        sys.exit

    global correlated

    if a in correlated and b in correlated[a]:
        return correlated[a][b]
    if b in correlated and a in correlated[b]:
        return correlated[b][a]

    val=sum(map(lambda (x,y):abs(poldiff(x,y)),zip(a,b)))

    correlated[a]={}
    correlated[a][b]=val

    correlated[b]={}
    correlated[b][a]=val

    return val

def cmp_score(x,y):
    xsc=x['score']
    ysc=y['score']
    
    if xsc>ysc:
        return +1
    elif xsc<ysc:
        return -1
    else:
        return 0

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

    gap=5
    
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

def proportion(data,sec):
    return sec['len']/len(data['tot'])

def score_cmp(x,y):
    xsc=y[0]
    ysc=x[0]

    if xsc>ysc:
        return +1
    elif xsc<ysc:
        return -1
    else:
        return 0

def stroke_difference(a,b):
    ret=[]
    len_a=len(a['sec'])
    len_b=len(b['sec'])

    if len_a>len_b:
        most,len_most=a,len_a
        least,len_least=b,len_b
    else:
        most,len_most=b,len_b
        least,len_least=a,len_a

    mosttotallen=len(most['tot'])
    leasttotallen=len(least['tot'])

    # and this think needs to be a function called stroke match or something
    for offset in range(len_most-len_least+1):
        loghi=minint
        loglo=maxint
        accmostlen=0.0
        accleastlen=0.0
        accscore=0.0
        for scan in range(len_least):
            score=correlate(most['sec'][offset+scan]['resampled'],least['sec'][scan]['resampled'])
            accscore+=score

            mostlen=most['sec'][offset+scan]['len']
            accmostlen+=mostlen

            leastlen=least['sec'][scan]['len']
            accleastlen+=leastlen

            lograt=numpy.log(float(mostlen)/float(leastlen))
            
            if lograt>loghi:
                loghi=lograt

            if lograt<loglo:
                loglo=lograt

        logscale=loghi-loglo
        leastrat=accleastlen/leasttotallen
        mostrat=accmostlen/mosttotallen

        final_score=accscore/((leastrat*mostrat)**3)
        
        ret.append(final_score)
    return ret

def multipart_letter_difference(a,b):
    a_item=a['item']
    b_item=b['item']
    if len(a_item)!=len(b_item):
        print 'array length mismatch in multipart_letter_difference'
        sys.exit()
    ret=[]
    for perm in itertools.permutations(a_item):
        score=0
        for a_stroke,b_stroke in zip(b_item,perm):
            pprint.pprint(a_stroke)
            pprint.pprint(b_stroke)
            score+=sorted(stroke_difference(a_stroke,b_stroke))[0]
        ret.append(score)
    
    return ret

def stroke_to_points_set(stroke):
    ret=[]
    for index in range(len(stroke)):
        if index==0:
            x0,y0=stroke[index]['pos']
        else:
            x1,y1=stroke[index]['pos']
            ret.extend(line_points(x0,y0,x1,y1))
            x0,y0=x1,y1
    return set(ret)

def strokes_append(data):
    global last_data
    sparkline_filter(data)

    ret=[]

    last_data=data

    multipart_letter=None
    for stroke in strokes:
        pprint.pprint(stroke['stroke'])
#       print stroke_to_points_set(stroke['stroke'])
        if bbox_overlap(data['bbox'],stroke['bbox']):
            # might be good to memoize the generated point sets
            if stroke_to_points_set(data['stroke']) & stroke_to_points_set(stroke['stroke']):
                multipart_letter=stroke['letter']

    if multipart_letter:
        multipart_letter['item'].append(data)
        data['letter']=multipart_letter

        multipart_letter_len=len(multipart_letter['item'])

        for letter in letters:
            if letter is multipart_letter:
                continue
            if len(letter['item'])!=multipart_letter_len:
                continue
            scores=multipart_letter_difference(multipart_letter,letter)
            for score in scores:
                ret.append((score,0,letter))
        ret.sort(score_cmp)
        for (score,item,letter) in ret:
            if 'char' in letter and 'type' in letter['char'] and letter['char']['type']=='told':
                print score,letter['char']['val']
    else:
        for letter in letters:
            item=letter['item'][0]
            scores=stroke_difference(data,item)
            for score in scores:
                ret.append((score,item,letter))
        ret.sort(score_cmp)

        new_letter={}
        new_letter['item']=[data]

        for (score,item,letter) in ret:
            if 'char' in letter and 'type' in letter['char'] and letter['char']['type']=='told':
                print score,letter['char']['val']

                new_letter['char']={}
                new_letter['char']['type']='guess'
                new_letter['char']['val']=letter['char']['val']

        data['letter']=new_letter

        letters.append(new_letter)
    strokes.append(data)
        
    #   now we can see the multi stroke letters
    #   look through the letters and find multi section letters with the same number of parts, at least for a start
    #   for each of these 
    #       try a multi section letter match 
    #       score on 
    #           best section matches
    #           factor in the size ratios after best section matches
    #       find the best letter matches

    #       need to be careful of strike through


def main():
    global current_stroke
    global orgx
    global orgy
    global sel
    global sel_w
    global sel_h
    global selected_letter
    global do_letters

    dorg=(0,0)
    drag=0
    down=0
    pygame.display.flip()
    startpos={}

    while True:
        refresh=1
        e=pygame.event.wait()
        if e.type == pygame.QUIT:
            return

        pressed=pygame.mouse.get_pressed()

        if e.type == pygame.KEYDOWN:
            if e.unicode and selected_letter:
                if e.unicode == u'\r':
                    if 'char' in selected_letter and 'type' in selected_letter['char'] and selected_letter['char']['type']=='guess':
                        selected_letter['char']['type']='told'
                else:
                    selected_letter['char']={'val':e.unicode,'type':'told'}
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
            selected_letter=find_letter(((sel[0]+orgx,sel[1]+orgy),(e.pos[0]+orgx,e.pos[1]+orgy)))

            do_letters=0
            
            sel_w=e.pos[0]-sel[0]
            sel_h=e.pos[1]-sel[1]

        if e.type == pygame.MOUSEBUTTONDOWN and e.button==2:
            drag=1
            dorg=e.pos
        elif e.type == pygame.MOUSEBUTTONUP and e.button==2:
            drag=0

        if e.type == pygame.MOUSEBUTTONDOWN and e.button==1:
            down=1
            current_stroke=[]
            current_stroke_append(e.pos)
            startpos=e.pos
        elif e.type == pygame.MOUSEBUTTONUP and e.button==1:
            down=0
            current_stroke_append(e.pos)
            if len(current_stroke) and startpos!=e.pos:
                strokes_append({'stroke':current_stroke,'bbox':bbox(current_stroke)})
        elif e.type == pygame.MOUSEMOTION:
            if drag:
                x=dorg[0]-e.pos[0]
                y=dorg[1]-e.pos[1]
                orgx+=x
                orgy+=y
                dorg=e.pos
            elif down:
                refresh=0
                current_stroke_append(e.pos)
                stroke_render(current_stroke,ink)
                pygame.display.update()
                
        if refresh:
            render()

import pickle

if len(sys.argv)>=2:
    filename=sys.argv[1]
    if os.path.exists(filename):
        f=open(filename)
        u=pickle.Unpickler(f)
        inobj=u.load()
        strokes=inobj['strokes']
        letters=inobj['letters']
        orgx=inobj['orgx']
        orgy=inobj['orgy']

screen=pygame.display.set_mode((width,height))
pygame.font.init()
font=pygame.font.Font(None, 20)
render()

main()

if len(sys.argv)==3:
    filename=sys.argv[2]
    if os.path.exists(filename):
        f=open(filename,'w')
    outobj={}
    outobj['strokes']=strokes
    outobj['letters']=letters
    outobj['orgx']=orgx
    outobj['orgy']=orgy
    pickle.dump(outobj,f)
