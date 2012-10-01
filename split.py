import sys
import line
import utils
import angles

maxint=sys.maxint
minint=-sys.maxint-1

def clean_distangle(graph):
    # this resamples the distance angle line and fully populates it for integer distances along the line
    # actually, it looks as if it returns a list of tuples of distance and angle, the distance part may be unnecessary
    minx=maxint
    maxx=minint
    scale=100.0
    points={} # hash to record all of the interpolated point
    for i in range(0,len(graph)-1): # go through all of the line sections in the distance angle graph
        x0=int(graph[i+0][0])
        y0=int(scale*graph[i+0][1])
        x1=int(graph[i+1][0])
        y1=int(scale*graph[i+1][1])
        for (x,y) in line.points(x0,y0,x1,y1): # convert the line section to points
            ix=int(x) # find the x position as an integer

            # we need to know where the line starts and ends
            # in all porbablility this will start at zero and go up to the total length of the stroke
            if ix>maxx:
                maxx=ix
            if ix<minx:
                minx=ix

            # points is an array bins of the angle value at any given integer distance from the start of the stroke
            if ix in points:
                points[ix].append(y/scale) # add a value to an existing bin
            else:
                points[ix]=[y/scale] # create a new bin

    # this is going to hold a clean, fully populated distance angle graph
    # means are used when the bins contain more than one value
    # any gaps are filled in with the last value seen
    ret=[]

    last=utils.mean(points[minx])
    for x in range(minx,maxx+1): # iterate over the entire range, there will be no gaps in this clean resampler
        if x in points: 
            m=utils.mean(points[x])
            ret.append(m)
            last=m
        else:
            ret.append(last)
    return ret;

def gap_delta(gap,points):
    delta=[]

    scale=1000.0

    # header, call it no gap
    for i in range(gap):
        delta.append(0)

    # in the middle of the range add a new element to the array at each distance point
    # this is the angle difference between the points at gap plus this distance and gap minus this difference
    for i in range(gap,len(points)-gap):
        # arg is just a scaled up version of the angle difference across twice the gap
        # we need integers for the upcoming median filter to make sense
        delta.append(int(scale*abs(angles.poldiff(points[i-gap],points[i+gap]))))

    # tailer, again no gap
    for i in range(len(points)-gap,len(points)):
        delta.append(0)

    # here is some smoothing of the difference data, see how it is actually proportinal to the gap
    # note the scale removal
    return [x/scale for x in utils.bucket(delta,(2*gap)/gap+1,utils.med)]

def salient(points):
    # welcome to heuristics city
    # really this needs to return a failure condition, there are many places where failure can occur and we need to know
    graph=angles.distangle(points)

    if len(graph)<2:
        # careful, not added products to data at this point
        return {}

    uniq_points=clean_distangle(graph)

    # we are looking for points of inflection
    gap=3
    if len(uniq_points)<=2*gap:
        return {}

    median_filtered=gap_delta(gap,uniq_points)

    # this bit is the slicer
    nsample=16
    threshold=2.0
    sec=[]
    acc=[]
    state='up'

    for i in range(0,len(uniq_points)):
        y=uniq_points[i]
        t=median_filtered[i]<threshold

        if state=='up' and not t:
            sec.append({'len':len(acc),'resampled':utils.resample(acc,nsample)})
            state='down'
        elif state=='down' and t:
            acc=[]
            state='up'
        if state=='up':
            acc.append(y)
    if acc:
        sec.append({'len':len(acc),'resampled':utils.resample(acc,nsample)})

    ret={}
    ret['sec']=sec
    ret['len']=len(uniq_points)
    
    return ret

