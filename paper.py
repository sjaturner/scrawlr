# copyright 2012, simon turner, sjaturner@googlemail.com all rights reserved
# for the moment, at least
#
#   Instructions
#   ============
#   
#   This rather nasty python module is able to identify hand written text. 
#   I'm using a Wacom pad for writing but a mouse will do. 
#
#   The program is a step towards the web hosted "single large canvas on 
#   which you write everything". This application will be written in 
#   Javascript and will save data to and load from a host using JASON. 
#   I think that this will play well with the inevitable stylus-based pads 
#   which are always just around the corner.
#
#   The python program is called paper.py. It implements a fairly large canvas. 
#   Sessions can be saved and loaded to and from files nominated on the command 
#   line. The following invocations are permitted.
#   
#       1. python paper.py
#       2. python paper.py null output
#       3. python paper.py input output
#       3. python paper.py input 
#
#   Case [1] starts a new session with no provision to save the canvas. Case [2] 
#   starts a new blank canvas and will save the result to output - for reasons 
#   which I've not investigated output has to be a file already (touch the file).
#   Case [3] takes an existing canvas. The changes made during the session will 
#   be saved to the named output file. Finally Case [4] takes an existing canvas 
#   with no provision to save.
#
#   The code knows nothing about written letters and their relationship to 
#   characters. It needs to be taught. 
#   
#   Suggested approach
#   ==================

#   Start a new session but capture the output (Case [2]). 
#   Use the pointing device on your computer to write the letters 'a' through 'z'.
#   If you are using a mouse then the left button is pen down. Next, use the right 
#   button to draw a red box around each letter in turn and hit the key which 
#   matches that letter. You'll notice that when the right mouse button is 
#   pressed then the letters associated with each character are displayed at 
#   the top left corner of the letters bounding box. Red letters are ones 
#   which the program has been told about.
#
#   Now use the mouse to copy one of the letters which you've already entered.
#   The program will try to find a close match. Next time you press the right 
#   mouse button you will see the closest match, or guess, in green - again at 
#   the top left bounding box position.
#
#   At present you need to confirm the guess or inform the program of the actual 
#   letter. This is another right hand button box exercise. In theory, the more 
#   letters you have identified, the better the subsequent matches.
#
#   You may scroll the canvas around by grabbing it with the middle mouse 
#   button.
#   
#   There is support for multi-part letters too, think 't', etc.
#
#   Method for identifying letters
#   ==============================
#
#   In brief: Each stroke is converted into a bearing/distance representation.
#   Rapid changes in bearing (corresponding to points where the pen direction 
#   alters quickly, the bottom of a 'v' for instance) are identified and the 
#   strokes are spit into sections based on this. For each section the bearing/
#   distance representation is normalised to a fixed length. These fixed length 
#   sequences can be correlated with sections from other strokes and match value 
#   can be associated with any pair of sections. I've arrived at a suitable 
#   heuristic after some experimentation. Sequences of sections are matched 
#   so that letter strokes may be compared. This process also takes account 
#   of the relative lengths of the sections and the proportion of the stroke 
#   over which the match takes place. There is considerable room for 
#   improvement here. The experimental approach is time consuming - a better 
#   method would be to run systematic tests on a large corpus of letters.
#   
#   Multipart characters are compared in terms of their component strokes. 
#   A permutation based approach is used to achieve the best match.
#
#   Improvements
#   ============
#   
#   Usability will be improved by a method for iterating rapidly across 
#   guessed or unidentified letters. After boxing a single character and 
#   identifying it the box will moved to the next uncertain character.
#
#   This program slows down after a while. Optimisations are required. 
#   Perhaps one could match against the best set of matching characters first?
#   The best performing matchers are fairly easily identified.
#
#   There is no concept of word, lines or spaces just yet. 
#
#   I'd like some sort of command interface which projects into the 
#   canvas. What could be more natural than a feature which allows 
#   someone to write ":!grep simon" and have all of the lines containing 
#   "simon" displayed below. All text output from commands could be 
#   rendered in your own typeface. Some sort of access to the underlying 
#   code would be nice, as would the ability to extend the interface - 
#   all in the canvas. A good query language would help.
#
#   Oh, and crashing less would be nice too.
#
# --- notes
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

#   next, a mode for quickly confirming guess letters
#       select a letter 
#       told it a key
#       box moves on to next sequential guess or unknown letter
#       need to be able to give word names to things
#           box
#           triangle
#       delimiters might be colon and semicolon
#           colon start a name and semicolon ends it
#       escape exits from this naming mode

import sys
sys.dont_write_bytecode = True
import os
import time
import pygame
import random
import simplejson
import pprint
import numpy
import itertools
import line
import utils
import bounding_box
import angles
import split
import differences

width=1024
height=768
ink_colour=(0,0,0)
paper_colour=(255, 255, 255)
red_colour=(255, 0, 0)
green_colour=(0,255,0)
line_colour=(255-0x40, 255-0x40, 255-0x40)
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

def paper_time():
    return time.time()
    
def stroke_render(s,colour):
    pointlist=[]
    if len(s)<2:
        return
    for item in s:
        x=item[0]-orgx
        y=item[1]-orgy
        pointlist.append((x,y))
    pygame.draw.lines(screen,colour,False,pointlist,1)

#last_data=None # just used to show the normalised angle data for the most recent stroke

#def section_render(section,x,y,colour):
#    pygame.draw.rect(screen,ink_colour,((x,y),(32,int(4*numpy.pi))),1)
#    off=0
#    for val in section:
#        lx=int(x+off*2)
#        ly=int(y+2*(val%(2*numpy.pi)))
#        pygame.draw.circle(screen,colour,(lx,ly),1,0)
#        off+=1

def find_letter(bbox): # becomes some sort of iterator perhaps
    for letter in letters:
        for item in letter['item']:
            if bounding_box.contains(bbox,item['bbox']):
                return letter
    return None
    
def render_char(x,y,c,colour): # renders the characters near the letter
    x-=orgx
    y-=orgy
    text = font.render('%c'%c,0,colour)
    textrect = text.get_rect()
    textrect.centerx=x
    textrect.centery=y
    pygame.draw.rect(screen,paper_colour,textrect)
    screen.blit(text,textrect)

def render():
    global font
    linegap=40
    colgap=width
    screen.fill(paper_colour)

#    if last_data:
#        ix=0
#        for sec in last_data['sec']:
#            section_render(sec['resampled'],ix,0,0x80)
#            ix+=34

    for y in range(0,height,linegap):
        oy=y-orgy%linegap
        pygame.draw.lines(screen,line_colour,False,((0,oy),(width,oy)),1)

    for item in strokes:
        if 'colour' in item:
            colour=item['colour']
        else:
            colour=ink_colour
        stroke_render(item['stroke'],colour)

    for letter in letters:
        item=letter['item'][0]
        if do_letters and 'bbox' in item and 'char' in letter:
            bbox=item['bbox']
            if letter['char']['type']=='told':
                col=red_colour
            elif letter['char']['type']=='guess':
                col=green_colour
            else:
                col=ink_colour
            render_char(bbox[0][0],bbox[0][1],letter['char']['val'],col)

    if current_stroke:
        stroke_render(current_stroke,ink_colour)

    if sel and sel_w and sel_h:
        pygame.draw.rect(screen,(255,0,0),((sel[0],sel[1]),(sel_w,sel_h)),1)
     
    pygame.display.flip()

def current_stroke_append(pos):
    event={}
    x=pos[0]+orgx
    y=pos[1]+orgy
    event=(x,y)
    current_stroke.append(event)


def special_filter(data):
    val=split.salient(data['stroke'])
    print simplejson.JSONEncoder().encode(val)
    if not val:
        return 0
    else:
        data['sec']=val['sec']
        data['len']=val['len']
        return 1


def score_cmp(x,y):
    xsc=y[0]
    ysc=x[0]

    if xsc>ysc:
        return +1
    elif xsc<ysc:
        return -1
    else:
        return 0

def stroke_to_points_set(stroke):
    ret=[]
    for index in range(len(stroke)):
        if index==0:
            x0,y0=stroke[index]
        else:
            x1,y1=stroke[index]
            for xoff,yoff in ((+1,0),(-1,0),(0,+1),(0,-1)): # fatten
                ret.extend(line.points(x0+xoff,y0+yoff,x1+xoff,y1+yoff))
            x0,y0=x1,y1
    return set(ret)

def strokes_append(data):
#   global last_data
    if not special_filter(data):
        # probably too short
        return

    ret=[]
    data['time']=paper_time()

#   last_data=data

    multipart_letter=None
    for stroke in strokes:
#       pprint.pprint(stroke['stroke'])
#       print stroke_to_points_set(stroke['stroke'])
        if bounding_box.overlaps(data['bbox'],stroke['bbox']):
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
            for score in differences.multipart(multipart_letter['item'],letter['item']):
                ret.append((score,letter))
        ret.sort(score_cmp)
        for (score,letter) in ret:
            if 'char' in letter and 'type' in letter['char'] and letter['char']['type']=='told':
                print 'm',score,letter['char']['val']

                multipart_letter['char']={}
                multipart_letter['char']['type']='guess'
                multipart_letter['char']['val']=letter['char']['val']
    else:
        for letter in letters:
            item=letter['item'][0]
            for score in differences.stroke(data,item):
                ret.append((score,letter))
        ret.sort(score_cmp)

        new_letter={}
        new_letter['item']=[data]

        for (score,letter) in ret:
            if len(letter['item'])!=1:
                continue

            if 'char' in letter and 'type' in letter['char'] and letter['char']['type']=='told':
                print 'u',score,letter['char']['val']

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
                strokes_append({'stroke':current_stroke,'bbox':bounding_box.make(current_stroke)})
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
                stroke_render(current_stroke,ink_colour)
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

