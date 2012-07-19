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
