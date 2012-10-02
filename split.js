phantom.injectJs('line.js')
phantom.injectJs('utils.js')
function clean_distangle(graph){
   var minx=Number.MAX_VALUE;
   var maxx=Number.MIN_VALUE;
   var scale=100;
   var points=new Object();
   var i=0;

   var x0=0;
   var y0=0;
   var x1=0;
   var y1=0;

   var line=[];
   var j=0;
   var x=0;
   var y=0;
   var ix=0;
   var ys=0;

   var ret=[];
   var last=0;
   var m=0;

   for(i=0;i<graph.length-1;++i){
      x0=graph[i+0][0]|0;
      y0=(scale*graph[i+0][1])|0;
      x1=graph[i+1][0]|0;
      y1=(scale*graph[i+1][1])|0;

      line=line_points(x0,y0,x1,y1); /* there is something very inefficient here */

      for(j=0;j<line.length;++j){
         x=line[j][0];
         y=line[j][1];

         ix=x|0;

         if(ix>maxx){
            maxx=ix;
         }

         if(ix<minx){
            minx=ix;
         }

         ys=(y/scale)|0;

         if(points.hasOwnProperty(ix)){
            points[ix].push(ys);
         }
         else{
            points[ix]=[ys];
         }
      }
   }

   last=mean(points[minx]);

   for(x=minx;x<maxx+1;++x){
      console.log(x);
      console.log('   '+points[x]);
      if(points.hasOwnProperty(x)){
         m=mean(points[x]);
         ret.push(m);
         last=m;
      }
      else{
         ret.push(m);
      }
   }

   return ret;
}

/*
console.log(clean_distangle([[0,0],[10,10],[20,10]]));
*/

input=[[308, 107], [308, 105], [306, 103], [302, 100], [297, 97], [291, 95], [283, 93], [275, 92], [267, 92], [258, 93], [248, 96], [239, 99], [231, 102], [225, 106], [223, 111], [223, 115], [223, 119], [224, 123], [227, 131], [233, 139], [241, 147], [250, 154], [259, 159], [266, 164], [271, 169], [274, 175], [275, 181], [275, 188], [274, 193], [272, 197], [267, 202], [261, 206], [250, 212], [237, 215], [219, 218], [200, 218], [184, 218], [172, 216], [162, 213], [156, 210], [152, 207], [151, 205], [150, 204], [150, 203], [150, 203]]

phantom.exit();
