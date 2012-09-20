def med(a):
    return sorted(a)[len(a)/2]

def bucket(samples,gap,fun):
    if not gap%2:
        sys.exit()
    extended=[samples[0]]*(gap/2)+samples+[samples[-1]]*(gap/2)
    ret=[]
    for i in range(0,len(samples)):
        ret.append(fun(extended[(i):(i+gap)]))
    return ret
   
correlated={}

def correlate(a,b,deltafun): # memoize this
    if len(a)!=len(b):
        print 'correlate only works for matched length sections'
        sys.exit

    global correlated

    if a in correlated and b in correlated[a]:
        return correlated[a][b]
    if b in correlated and a in correlated[b]:
        return correlated[b][a]

    val=sum(map(lambda (x,y):abs(deltafun(x,y)),zip(a,b)))

    correlated[a]={}
    correlated[a][b]=val

    correlated[b]={}
    correlated[b][a]=val

    return val

def resample(a,n):
    while len(a)<64:
        a=[val for val in a for x in (0, 1)]

    step=float(len(a))/float(n)
    base=0.0
    ret=[]
    while base<len(a):
        slice=a[int(base):int(base+step)]
        base+=step;
        slice.sort() # looks as if this is unnecessary
        ret.append(med(slice)) 
    return tuple(ret)

def mean(a):
    return sum(a)/len(a)

if __name__ == "__main__":
    print bucket([1,2,9,4,5,6],5,med)
