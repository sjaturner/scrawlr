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
   
if __name__ == "__main__":
    print bucket([1,2,9,4,5,6],5,med)
