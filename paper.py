import sys
import time
import pygame
import random
import simplejson

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

def roundline(srf, ink, start, end, radius=1):
    dx=end[0]-start[0]
    dy=end[1]-start[1]
    distance=max(abs(dx), abs(dy))
    for i in range(distance):
        x=int( start[0]+float(i)/distance*dx)
        y=int( start[1]+float(i)/distance*dy)
        pygame.draw.circle(srf, ink, (x, y), radius)

record=[]
stroke={}

def render():
    pygame.display.flip()
    pass

def main():
    draw_on=False
    last_pos=(0,0)
    radius=10
    pygame.display.flip()
    last_pressed=(0,0,0)

    while True:
        e=pygame.event.wait()
        print pygame.mouse.get_pressed()
        if e.type == pygame.QUIT:
            sys.exit()

        if e.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.circle(screen, ink, e.pos, radius)
            draw_on=True
        elif e.type == pygame.MOUSEBUTTONUP:
            draw_on=False
        elif e.type == pygame.MOUSEMOTION:
            if draw_on:
                screen.fill(paper)
                pygame.draw.circle(screen, ink, e.pos, radius)
                roundline(screen, ink, e.pos, last_pos,  radius)
            last_pos=e.pos
        last_pressed=pygame.mouse.get_pressed()

        render()

if len(sys.argv)==1:
    filename=str(int(time.time()))+'.paper'
else:
    for file in sys.argv:
        print file
    
screen=pygame.display.set_mode((800,600))
screen.fill(paper)

main()
