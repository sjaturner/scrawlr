import sys

maxint=sys.maxint
minint=-sys.maxint-1

def contains(outer,inner):
    (outer_tl_x,outer_tl_y)=outer[0]
    (outer_br_x,outer_br_y)=outer[1]

    (inner_tl_x,inner_tl_y)=inner[0]
    (inner_br_x,inner_br_y)=inner[1]

    return outer_tl_x<inner_tl_x and outer_tl_y<inner_tl_y and outer_br_x>inner_br_x and outer_br_y>inner_br_y

def overlaps(a,b):
    (a_tl_x,a_tl_y)=a[0]
    (a_br_x,a_br_y)=a[1]
    
    (b_tl_x,b_tl_y)=b[0]
    (b_br_x,b_br_y)=b[1]

    if a_tl_x>b_br_x or a_br_x<b_tl_x or a_tl_y>b_br_y or a_br_y<b_tl_y:
        return False
    else:
        return True

def make(s):
    minx=maxint
    miny=maxint
    maxx=minint
    maxy=minint
    for item in s:
        x,y=item
        if x<minx:
            minx=x
        if y<miny:
            miny=y
        if x>maxx:
            maxx=x
        if y>maxy:
            maxy=y
    return ((minx,miny),(maxx,maxy))
    

if __name__ == "__main__":
    pass
