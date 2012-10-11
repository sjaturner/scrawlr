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

    mosttotallen=most['len']
    leasttotallen=least['len']

    # and this think needs to be a function called stroke match or something
    for offset in range(len_most-len_least+1):
        loghi=minint
        loglo=maxint
        accmostlen=0.0
        accleastlen=0.0
        accscore=0.0
        for scan in range(len_least):
            score=utils.correlate(most['sec'][offset+scan]['resampled'],least['sec'][scan]['resampled'],angles.poldiff)
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
        leastrat=accleastlen/(1+leasttotallen)
        mostrat=accmostlen/(1+mosttotallen)

        # high final score is bad
        # high accscore is bad

        if leastrat==0 or mostrat==0:
            final_score=maxint
        else:
            final_score=(1+logscale)*accscore/((leastrat*mostrat)**3)
        
        ret.append(final_score)
    return ret

def multipart(a,b):
    a_item=a['item']
    b_item=b['item']
    if len(a_item)!=len(b_item):
        print 'array length mismatch in multipart_letter_difference'
        sys.exit()
    ret=[]
    for perm in itertools.permutations(a_item):
        score=0
        for a_stroke,b_stroke in zip(b_item,perm):
#           pprint.pprint(a_stroke)
#           pprint.pprint(b_stroke)
            score+=sorted(stroke(a_stroke,b_stroke))[0]
        ret.append(score)
    
    return ret

