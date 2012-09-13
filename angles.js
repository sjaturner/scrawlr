function distangle(stroke){
   var first=1;
   var fangle=1;
   var acc_x=0;
   var ret=[];
   var index=0;
   var pi=Math.PI;
   var old_x;
   var old_y;

   for(index=0;index<stroke.length;++index){
      var pos=stroke[index].pos;
      var x=pos[0]
      var y=pos[1]

      if(first){
         first=0;
      }
      else{
         var dx=x-old_x;
         var dy=y-old_y;
         var r=Math.sqrt(dx*dx+dy*dy);
         if(r>0){
            var angle=0;
            var old_t=0;

            acc_x+=r;
            t=Math.atan(dy,dx)
            if(fangle){
               fangle=0;
               angle=t;
               old_t=t;
            }
            else{
               var delta_t=t-old_t;
               
               if(delta_t<pi){
                  delta_t+=2*pi;
               }
               if(delta_t>pi){
                  delta_t-=2*pi
               }
               angle+=delta_t;
            }
            ret.push([acc_x|0,angle]);
         }
      }

      old_x=x;
      old_y=y;
   }
   return ret;
}

s=[{pos:[0,0]},{pos:[10,10]},{pos:[20,20]},{pos:[30,20]}]

console.log(distangle(s))

phantom.exit();