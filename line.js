"use strict";

function points(x0,y0,x1,y1){
   var sx=0;
   var sy=0;
   var a=[];
   var steep=false;
   var tv=0;
   var deltax=0;
   var deltay=0;
   var error=0;
   var y=0;
   var x=0;
   var ystep=0;

   x0=x0|0;
   y0=y0|0;
   x1=x1|0;
   y1=y1|0;

   sx=x0;
   sy=y0;

   steep=Math.abs(y1 - y0)>Math.abs(x1 - x0)

   if(steep){
      tv=x0;
      x0=y0;
      y0=tv;

      tv=x1;
      x1=y1;
      y1=tv;
   }

   if(x0 > x1){
      tv=x0;
      x0=x1;
      x1=tv;

      tv=y0;
      y0=y1;
      y1=tv;
   }

   if(y0<y1){
      ystep=+1;
   }
   else{
      ystep=-1;
   }

   deltax=(x1-x0)|0;
   deltay=Math.abs(y1-y0);
   error=Math.floor(-deltax/2);

   y=y0;

   for(x=x0;x<=x1;x=(x+1)|0){
      if(steep){
         a.push([y,x]);
      }
      else{
         a.push([x,y]);
      }

      error=error+deltay;
      if(error>0){
         y=(y+ystep)|0;
         error=(error-deltax)|0;
      }
   }

   x=a[0][0];
   y=a[0][1];

   if((x|0)===(sx|0) && (y|0)===(sy|0)){
   }
   else{
      a.reverse();
   }

   return a;
}

var a=points(10,10,20,20);
var i=0;

for(i=0;i<a.length;++i){
   console.log(a[i]);
}
phantom.exit();
