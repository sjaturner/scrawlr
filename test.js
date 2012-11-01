phantom.injectJs('engine.js');

function line_to_fattened_point_array(xo,yo,xn,yn){
   var line=line_points(xo,yo,xn,yn);
   var ret=[];
   var i;
   var x;
   var y;

   for(i=0;i<line.length;++i){
      x=line[i][0];
      y=line[i][1];

      ret.push([x+0,y+0]);

      ret.push([x+0,y+1]);
      ret.push([x+0,y-1]);
      ret.push([x+1,y+0]);
      ret.push([x-1,y+0]);
   }

   return ret;
}

function stroke_to_point_set(stroke){
   var i;
   var first=1;
   var xo=0;
   var yo=0;
   var xn=0;
   var yn=0;
   var ret={};
   var a=[];
   var ia;

   for(i=0;i<stroke.length;++i){
      if(first){
         xo=stroke[i][0];
         yo=stroke[i][1];

         first=0;
      }
      else{
         xn=stroke[i][0];
         yn=stroke[i][1];

         a=line_to_fattened_point_array(xo,yo,xn,yn);

         for(ia=0;ia<a.length;++ia){
            key=''+a[ia][0]+'_'+a[ia][1];
            ret[key]=1;
         }
         
         xo=xn;
         yo=yn;
      }
   }

   return ret;
}

function intersects(a,b){
   var ka;
   var kb;

   for(ka in a){
      for(kb in b){
         if(ka==kb){
            return 1;
         }
      }
   }

   return 0;
}

stroke=[[1,1],[10,10]]
console.log(JSON.stringify(stroke_to_point_set(stroke)));
ps=stroke_to_point_set(stroke);
console.log(intersects(stroke_to_point_set([[1,1],[10,10]]),stroke_to_point_set([[3,1],[14,10]])));
phantom.exit();
