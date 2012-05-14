import sys
import time
import pygame
import random
import simplejson
import pprint

#event
# point 
#  x
#  y
# time

#stroke 
# start event (uid)
# list delta event 
# bbox

#record
# list stroke

ink=(0,0,0)
paper=(255, 255, 255)

record=[]

def render():
    screen.fill(paper)
    for s in record:
        pointlist=[]
        for item in s:
            pointlist.append(item['pos'])
        pygame.draw.lines(screen,ink,False,pointlist,1)
    pygame.display.flip()
    pass

def main():

    stroke=[]
    radius=10
    pygame.display.flip()
    last_pressed=(0,0,0)

    while True:
        e=pygame.event.wait()
        print pygame.mouse.get_pressed()
        if e.type == pygame.QUIT:
            pprint.pprint(record)
            sys.exit()

        pressed=pygame.mouse.get_pressed()
        if e.type == pygame.MOUSEBUTTONDOWN:
            if not last_pressed[0] and pressed[0]:
                stroke=[]
                event={}
                event['time']=time.time()
                event['pos']=e.pos
                stroke.append(event)
        elif e.type == pygame.MOUSEBUTTONUP:
            if last_pressed[0] and not pressed[0]:
                event={}
                event['time']=time.time()
                event['pos']=e.pos
                stroke.append(event)
                record.append(stroke)
        elif e.type == pygame.MOUSEMOTION:
            if pressed[0]:
                event={}
                event['time']=time.time()
                event['pos']=e.pos
                stroke.append(event)
                
        last_pressed=pressed

        render()

if len(sys.argv)==1:
    filename=str(int(time.time()))+'.paper'
else:
    for file in sys.argv:
        print file
    
screen=pygame.display.set_mode((800,600))
screen.fill(paper)

print float(time.time())
main()
