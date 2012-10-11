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

            mostlen=most['sec'][offset+scan]['len']
            acc_most_len+=mostlen

            leastlen=least['sec'][scan]['len']
            acc_least_len+=leastlen

            lograt=numpy.log(float(mostlen)/float(leastlen))
            
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

