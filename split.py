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
    return ret

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

if __name__ == '__main__':
    print gap_delta(3,[1,1,1,1,1,1,1,1,1,1,1,1,1,2,-1,-1,-1,-1,-1,0,0,0,1,1,1,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3]);
    

#[(308, 107), (308, 105), (306, 103), (302, 100), (297, 97), (291, 95), (283, 93), (275, 92), (267, 92), (258, 93), (248, 96), (239, 99), (231, 102), (225, 106), (223, 111), (223, 115), (223, 119), (224, 123), (227, 131), (233, 139), (241, 147), (250, 154), (259, 159), (266, 164), (271, 169), (274, 175), (275, 181), (275, 188), (274, 193), (272, 197), (267, 202), (261, 206), (250, 212), (237, 215), (219, 218), (200, 218), (184, 218), (172, 216), (162, 213), (156, 210), (152, 207), (151, 205), (150, 204), (150, 203), (150, 203)]
#{'sec': [{'resampled': (-2.5449999999999999, -2.9350000000000001, -3.2400000000000002, -3.46, -4.3208333333333329, -5.0733333333333333, -5.4900000000000002, -5.7000000000000002, -5.2600000000000007, -4.4550000000000001, -3.7000000000000002, -3.395, -3.29, -3.1400000000000001, -3.0249999999999999, -2.6699999999999999), 'len': 336}], 'len': 336}

#[(410, 113), (410, 112), (411, 112), (412, 112), (413, 112), (416, 112), (421, 112), (432, 112), (447, 112), (462, 112), (480, 111), (499, 110), (518, 109), (534, 108), (547, 108), (557, 108), (562, 108), (566, 108), (567, 108), (566, 108), (565, 108), (564, 108), (563, 108), (562, 109), (559, 110), (551, 112), (535, 117), (508, 127), (490, 133), (475, 140), (453, 147), (420, 159), (406, 165), (398, 168), (393, 170), (389, 172), (390, 172), (394, 171), (401, 170), (432, 166), (469, 162), (507, 157), (547, 153), (585, 149), (613, 147), (628, 145), (639, 145), (644, 145), (646, 145), (645, 145), (645, 145)]
#{'sec': [{'resampled': (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.029999999999999999, -0.050000000000000003, -0.050000000000000003, -0.050000000000000003, -0.050000000000000003, -0.050000000000000003, -0.059999999999999998, -0.029999999999999999, 0.0, 0.0), 'len': 155}, {'resampled': (2.8300000000000001, 2.8799999999999999, 2.8399999999999999, 2.8100000000000001, 2.79, 2.79, 2.7999999999999998, 2.77, 2.7200000000000002, 2.7799999999999998, 2.8199999999999998, 2.8199999999999998, 2.7999999999999998, 2.79, 2.7400000000000002, 2.77), 'len': 184}, {'resampled': (-0.14999999999999999, -0.13, -0.12, -0.11, -0.10000000000000001, -0.11, -0.12, -0.13, -0.11, -0.089999999999999997, -0.089999999999999997, -0.10000000000000001, -0.089999999999999997, -0.080000000000000002, -0.10500000000000001, 0.0), 'len': 257}], 'len': 607}
