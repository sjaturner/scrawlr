import sys
import utils
import angles
import numpy
import itertools

maxint=sys.maxint
minint=-sys.maxint-1

def stroke(a,b):
    ret=[]
    len_a=len(a['sec'])
    len_b=len(b['sec'])

    if len_a>len_b:
        most,len_most=a,len_a
        least,len_least=b,len_b
    else:
        most,len_most=b,len_b
        least,len_least=a,len_a

    most_total_len=most['len']
    least_total_len=least['len']

    # and this think needs to be a function called stroke match or something
    for offset in range(len_most-len_least+1):
        log_hi=minint
        log_lo=maxint
        acc_most_len=0.0
        acc_least_len=0.0
        acc_score=0.0
        for scan in range(len_least):
            score=utils.correlate(most['sec'][offset+scan]['resampled'],least['sec'][scan]['resampled'],angles.poldiff)
            acc_score+=score

            most_len=most['sec'][offset+scan]['len']
            acc_most_len+=most_len

            least_len=least['sec'][scan]['len']
            acc_least_len+=least_len

            lograt=numpy.log(float(most_len)/float(least_len))
            
            if lograt>log_hi:
                log_hi=lograt

            if lograt<log_lo:
                log_lo=lograt

        logscale=log_hi-log_lo
        leastrat=acc_least_len/(1+least_total_len)
        mostrat=acc_most_len/(1+most_total_len)

        # high final score is bad
        # high acc_score is bad

        if leastrat==0 or mostrat==0:
            final_score=maxint
        else:
            final_score=(1+logscale)*acc_score/((leastrat*mostrat)**3)
        
        ret.append(final_score)
    return ret

def multipart(a,b):
    ret=[]
    for perm in itertools.permutations(a):
        score=0
        for b_stroke,a_stroke in zip(b,perm):
            score+=sorted(stroke(a_stroke,b_stroke))[0]
        ret.append(score)
    
    return ret
    
if __name__ == "__main__":
    a={'sec':({'len':155,'resampled':(0,0,0,0,0,0,-0.03,-0.05,-0.05,-0.05,-0.05,-0.05,-0.06,-0.03,0,0)},{'len':183,'resampled':(2.83,2.88,2.84,2.81,2.79,2.79,2.8,2.76,2.72,2.78,2.82,2.82,2.8,2.79,2.74,2.77)},{'len':256,'resampled':(-0.14,-0.13,-0.12,-0.11,-0.1,-0.11,-0.12,-0.12,-0.11,-0.09,-0.09,-0.1,-0.09,-0.08,-0.10500000000000001,0)}),'len':607}
    b={'sec':({'len':155,'resampled':(0,0,0,0,0,0,-0.03,-0.05,-0.05,-0.05,-0.05,-0.05,-0.06,-0.03,0,0)},{'len':183,'resampled':(2.83,2.88,2.84,2.81,2.79,2.79,2.8,2.76,2.72,2.78,2.82,2.82,2.8,2.79,2.74,2.77)},{'len':256,'resampled':(-0.14,-0.13,-0.12,-0.11,-0.1,-0.11,-0.12,-0.12,-0.11,-0.09,-0.09,-0.1,-0.09,-0.08,-0.10500000000000001,0)}),'len':607}
    c={'sec':({'len':155,'resampled':(0,0,0,0,0,0,-0.03,-0.05,-0.05,-0.05,-0.05,-0.05,-0.06,-0.03,0,0)},{'len':256,'resampled':(-0.14,-0.13,-0.12,-0.11,-0.1,-0.11,-0.12,-0.12,-0.11,-0.09,-0.09,-0.1,-0.09,-0.08,-0.10500000000000001,0)}),'len':607}

#   print stroke(a,c)

    a=[{'len': 127, 'stroke': [(531, 187), (532, 187), (535, 187), (542, 187), (559, 187), (574, 187), (586, 186), (597, 185), (607, 184), (615, 184), (622, 183), (629, 183), (635, 183), (640, 183), (645, 183), (649, 183), (653, 183), (656, 183), (657, 183), (658, 183), (658, 183)], 'sec': [{'resampled': (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.050000000000000003, -0.080000000000000002, -0.089999999999999997, -0.089999999999999997, -0.02, -0.095000000000000001, 0.0, 0.0, 0.0, 0.0), 'len': 127}], 'bbox': ((531, 183), (658, 187)), 'letter': {}, 'time': 1350153597.2683401}, {'len': 64, 'stroke': [(587, 181), (588, 181), (588, 183), (588, 185), (588, 187), (588, 189), (588, 190), (588, 192), (588, 194), (588, 196), (588, 197), (587, 200), (587, 203), (587, 206), (588, 210), (589, 213), (589, 216), (589, 220), (589, 223), (589, 226), (589, 229), (589, 232), (589, 236), (589, 239), (589, 241), (589, 242), (589, 243), (590, 243), (590, 243)], 'sec': [{'resampled': (1.3847499999999999, 1.5700000000000001, 1.5700000000000001, 1.5700000000000001, 1.7850000000000001, 1.6799999999999999, 1.5625, 1.3283333333333334, 1.4600000000000002, 1.5700000000000001, 1.5700000000000001, 1.5700000000000001, 1.5700000000000001, 1.5700000000000001, 1.5700000000000001, 1.5700000000000001), 'len': 64}], 'bbox': ((587, 181), (590, 243)), 'letter': {}, 'time': 1350153599.4100969}]
    b=[{'len': 166, 'stroke': [(197, 116), (199, 116), (203, 117), (209, 122), (216, 129), (222, 138), (232, 148), (242, 158), (254, 169), (267, 180), (276, 188), (283, 194), (290, 201), (298, 208), (306, 214), (312, 219), (317, 223), (320, 225), (320, 226), (319, 226), (319, 226)], 'sec': [{'resampled': (0.30500000000000005, 0.72999999999999998, 0.85499999999999998, 0.93999999999999995, 0.79500000000000004, 0.78000000000000003, 0.77000000000000002, 0.73999999999999999, 0.71999999999999997, 0.70999999999999996, 0.70999999999999996, 0.72999999999999998, 0.76000000000000001, 0.68999999999999995, 0.67000000000000004, 0.68000000000000005), 'len': 166}], 'bbox': ((197, 116), (320, 226)), 'letter': {}, 'time': 1350153594.0370569}, {'len': 146, 'stroke': [(319, 131), (318, 131), (317, 131), (314, 134), (308, 139), (299, 145), (291, 152), (282, 160), (273, 169), (264, 181), (256, 193), (249, 203), (242, 210), (238, 215), (236, 218), (235, 220), (234, 220), (234, 221), (233, 222), (230, 224), (225, 228), (221, 231), (219, 233), (218, 233), (218, 233)], 'sec': [{'resampled': (2.5499999999999998, 2.4399999999999999, 2.5299999999999998, 2.46, 2.4199999999999999, 2.3999999999999999, 2.3599999999999999, 2.2799999999999998, 2.2000000000000002, 2.1600000000000001, 2.1699999999999999, 2.25, 2.3049999999999997, 2.1742857142857139, 2.5, 2.48), 'len': 146}], 'bbox': ((218, 131), (319, 233)), 'letter': {}, 'time': 1350153595.265907}]

    print multipart(a,b);

