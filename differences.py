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

if __name__ == "__main__":
    a={'sec':({'len':155,'resampled':(0,0,0,0,0,0,-0.03,-0.05,-0.05,-0.05,-0.05,-0.05,-0.06,-0.03,0,0)},{'len':183,'resampled':(2.83,2.88,2.84,2.81,2.79,2.79,2.8,2.76,2.72,2.78,2.82,2.82,2.8,2.79,2.74,2.77)},{'len':256,'resampled':(-0.14,-0.13,-0.12,-0.11,-0.1,-0.11,-0.12,-0.12,-0.11,-0.09,-0.09,-0.1,-0.09,-0.08,-0.10500000000000001,0)}),'len':607}
    b={'sec':({'len':155,'resampled':(0,0,0,0,0,0,-0.03,-0.05,-0.05,-0.05,-0.05,-0.05,-0.06,-0.03,0,0)},{'len':183,'resampled':(2.83,2.88,2.84,2.81,2.79,2.79,2.8,2.76,2.72,2.78,2.82,2.82,2.8,2.79,2.74,2.77)},{'len':256,'resampled':(-0.14,-0.13,-0.12,-0.11,-0.1,-0.11,-0.12,-0.12,-0.11,-0.09,-0.09,-0.1,-0.09,-0.08,-0.10500000000000001,0)}),'len':607}
    c={'sec':({'len':155,'resampled':(0,0,0,0,0,0,-0.03,-0.05,-0.05,-0.05,-0.05,-0.05,-0.06,-0.03,0,0)},{'len':256,'resampled':(-0.14,-0.13,-0.12,-0.11,-0.1,-0.11,-0.12,-0.12,-0.11,-0.09,-0.09,-0.1,-0.09,-0.08,-0.10500000000000001,0)}),'len':607}

    print stroke(a,c)
