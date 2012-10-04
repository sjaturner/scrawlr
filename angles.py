import numpy

def distangle(stroke):
    first=1
    fangle=1
    acc_x=0
    ret=[]
    for event in stroke:
        pos=event
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
                print 'z',dx,dy,t

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

def poldiff(a,b):
    pi=numpy.pi
    ret=a-b
    while ret<-pi:
        ret+=2*pi
    while ret>+pi:
        ret-=2*pi
#   print  '   ',a,b,ret
    return ret

