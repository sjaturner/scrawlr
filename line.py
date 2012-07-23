def points(x0, y0, x1, y1):
   sx=x0
   sy=y0
   a=[]
   steep = abs(y1 - y0) > abs(x1 - x0)
   if steep:
      x0, y0 = y0, x0  
      x1, y1 = y1, x1

   if x0 > x1:
      x0, x1 = x1, x0
      y0, y1 = y1, y0
   
   if y0 < y1: 
      ystep = 1
   else:
      ystep = -1

   deltax = x1 - x0
   deltay = abs(y1 - y0)
   error = -deltax / 2
   y = y0

   for x in range(x0, x1 + 1): # We add 1 to x1 so that the range includes x1
      if steep:
         a.append((y, x))
      else:
         a.append((x, y))
            
      error = error + deltay
      if error > 0:
         y = y + ystep
         error = error - deltax
   
   (x,y)=a[0]
   if x==sx and y==sy:
      pass
   else:
      a.reverse()

   return a

def line_print(x0,y0,x1,y1):
    p=points(x0,y0,x1,y1)
    for (x,y) in p:
        print '%d,%d'%(x,y)
    
if __name__ == "__main__":
    line_print(+10,+10,+20,+20);
    line_print(-10,+10,+20,+20);
    line_print(-10,-10,+20,+20);
    line_print(-10,-10,-20,+20);
    line_print(-10,-10,-20,-20);
    line_print(1,7,7,-1);
    line_print(5,7,-2,2);
    line_print(0,-4,9,0);
    line_print(-1,9,2,-1);
    line_print(6,4,-8,6);
    line_print(8,-5,0,0);
    line_print(-6,-2,-4,-6);
    line_print(-9,-1,0,0);
    line_print(-9,0,0,4);
    line_print(-1,-8,0,4);
    line_print(-9,-7,9,4);
    line_print(-4,9,-1,3);
    line_print(-6,-6,9,1);
    line_print(-1,1,8,-5);
    line_print(6,8,8,-6);
    line_print(-3,-5,5,4);
    line_print(-3,-7,-1,4);
    line_print(7,7,-1,3);
    line_print(-9,-7,5,0);
    line_print(-4,2,-8,-6);
    line_print(0,0,0,0);
    line_print(1,1,1,1);
