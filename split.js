phantom.injectJs('line.js')
phantom.injectJs('utils.js')
phantom.injectJs('angles.js')

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

      line=line_points(x0,y0,x1,y1); /* there is something very inefficient here, the scaling creates loads of integer points - yeuch */

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

         ys=(y/scale);

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

function gap_delta(gap,points){
   var delta=[];
   var medians=[];
   var ret=[];
   var scale=1000.0;
   var i=0;

   for(i=0;i<gap;++i){
      delta.push(0);
   }

   for(i=gap;i<points.length-gap;++i){
      delta.push((scale*Math.abs(poldiff(points[i-gap],points[i+gap])))|0);
   }

   for(i=0;i<gap;++i){
      delta.push(0);
   }


   medians=bucket(delta,(2*gap)/gap+1,middle);

   for(i=0;i<medians.length;++i){
      ret.push(medians[i]/scale);
   }

   return ret;
}

function salient(points){
   var graph=distangle(points);
   var uniq_points;
   var gap=3;
   var median_filtered;

   var nsample=16;
   var threshold=2.0;
   var sec=[];
   var acc=[];
   var state='up';

   var i=0;
   var y=0;
   var t=0;

   if(graph.length<2){
      return {}
   }

   uniq_points=clean_distangle(graph);

   if(uniq_points.length<2*gap){
      return {}
   }

   median_filtered=gap_delta(gap,uniq_points);


   for(i=0;i<uniq_points.length;++i){
      y=uniq_points[i];

      t=median_filtered[i]<threshold;


      if(state=='up' && !t){
         sec.push({'len':acc.length,'resamples':resample(acc,nsample)});
         state='down';
      }
      else if(state=='down' && t){
         acc=[];
         state='up';
      }
      else{
         acc.push(y);
      }
   }
      

   if(acc.length){
      sec.push({'len':acc.length,'resamples':resample(acc,nsample)});
   }

   for(i=0;i<sec.length;++i){
   }


   return {'sec':sec,'len':uniq_points.length}
}


console.log(JSON.stringify(salient([[410, 113], [410, 112], [411, 112], [412, 112], [413, 112], [416, 112], [421, 112], [432, 112], [447, 112], [462, 112], [480, 111], [499, 110], [518, 109], [534, 108], [547, 108], [557, 108], [562, 108], [566, 108], [567, 108], [566, 108], [565, 108], [564, 108], [563, 108], [562, 109], [559, 110], [551, 112], [535, 117], [508, 127], [490, 133], [475, 140], [453, 147], [420, 159], [406, 165], [398, 168], [393, 170], [389, 172], [390, 172], [394, 171], [401, 170], [432, 166], [469, 162], [507, 157], [547, 153], [585, 149], [613, 147], [628, 145], [639, 145], [644, 145], [646, 145], [645, 145], [645, 145]])));

/*
console.log(salient([[308, 107], [308, 105], [306, 103], [302, 100], [297, 97], [291, 95], [283, 93], [275, 92], [267, 92], [258, 93], [248, 96], [239, 99], [231, 102], [225, 106], [223, 111], [223, 115], [223, 119], [224, 123], [227, 131], [233, 139], [241, 147], [250, 154], [259, 159], [266, 164], [271, 169], [274, 175], [275, 181], [275, 188], [274, 193], [272, 197], [267, 202], [261, 206], [250, 212], [237, 215], [219, 218], [200, 218], [184, 218], [172, 216], [162, 213], [156, 210], [152, 207], [151, 205], [150, 204], [150, 203], [150, 203]]));
gap_delta(3,[1,1,1,1,1,1,1,1,1,1,1,1,1,2,-1,-1,-1,-1,-1,0,0,0,1,1,1,2,2,2,2,3,3,3,3,3,3,3,3,3,3,3,3,3]);
console.log(clean_distangle([[0,0],[10,10]]));
input=[[308, 107], [308, 105], [306, 103], [302, 100], [297, 97], [291, 95], [283, 93], [275, 92], [267, 92], [258, 93], [248, 96], [239, 99], [231, 102], [225, 106], [223, 111], [223, 115], [223, 119], [224, 123], [227, 131], [233, 139], [241, 147], [250, 154], [259, 159], [266, 164], [271, 169], [274, 175], [275, 181], [275, 188], [274, 193], [272, 197], [267, 202], [261, 206], [250, 212], [237, 215], [219, 218], [200, 218], [184, 218], [172, 216], [162, 213], [156, 210], [152, 207], [151, 205], [150, 204], [150, 203], [150, 203]]
console.log(line_points(0,0,10,10));
*/


phantom.exit();
