function intcmp(a,b){
   return a-b;
}

function middle(a){
   var sorted=a.sort(intcmp);

   return sorted[a.length>>1];
}

function even_integer(val){
   if(val<0){
      return false;
   }

   if(val!=(val|0)){
      return false;
   }

   if(val==((val>>1)<<1)){
      return false;
   }

   return true;
}

function bucket(samples,gap,fun){
   var i=0;
   var l=[];
   var r=[];
   var half_gap=0;
   var extended;
   var ret=[];

   if(!even_integer(gap)){
      return null;
   }

   half_gap=(gap/2)|0;

   for(i=0;i<half_gap;++i){
      l.push(samples[0]);
   }

   for(i=0;i<half_gap;++i){
      r.push(samples[samples.length-1]);
   }

   extended=l.concat(samples,r);

   for(i=0;i<samples.length;++i){
      ret.push(fun(extended.slice(i,i+gap)));
   }

   return ret;
}

function correlate(a,b,deltafun){
   var ret=0;
   var i=0;

   if(a.length!=b.length){
      /* can only correlate stuff which is the same length */
      return Number.MAX_VALUE; /* give this a really bad score */
   }

   for(i=0;i<a.length;++i){
      var delta=Math.abs(deltafun(a[i],b[i]));
      ret+=delta;
   }

   return ret;
}

function resample(a,n){
   var d=a;
   var i=0;
   var step=0;
   var base=0.0;
   var ret=[];
   var slice=[]

   while(a.length<64){
      d=[]
      for(i=0;i<a.length;++i){
         d.push(a[i]);
         d.push(a[i]);
      }
      a=d;
   }

   step=a.length/n;

   while(base<a.length){
      var slice=a.slice(base|0,(base+step)|0);
      ret.push(middle(slice));

      base+=step;
   }

   return ret;
}

function mean(a){
   var i=0;
   var sum=0;

   for(i=0;i<a.length;++i){
      sum+=a[i];
   }

   return sum/a.length;
}

function distangle(stroke){
   var first=1;
   var fangle=1;
   var acc_x=0;
   var ret=[];
   var index=0;
   var pi=Math.PI;
   var old_x;
   var old_y;
   var old_t=0;
   var angle=0;

   for(index=0;index<stroke.length;++index){
      var x=stroke[index][0]
      var y=stroke[index][1]

      if(first){
         first=0;
      }
      else{
         var dx=x-old_x;
         var dy=y-old_y;
         var r=Math.sqrt(dx*dx+dy*dy);
         if(r>0){

            acc_x+=r;

            t=Math.atan2(dy,dx)

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
            old_t=t;
         }
      }

      old_x=x;
      old_y=y;
   }
   return ret;
}

function poldiff(a,b){
   var pi=Math.PI;
   var ret=a-b;

   while(ret<-pi){
      ret+=2*pi;
   }
   while(ret>+pi){
      ret-=2*pi;
   }
   return ret
}

function line_points(x0,y0,x1,y1){
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

   steep=Math.abs(y1 - y0)>Math.abs(x1 - x0);

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

function bounding_box_contains(outer,inner){
    var outer_tl_x=outer[0][0];
    var outer_tl_y=outer[0][1];

    var outer_br_x=outer[1][0];
    var outer_br_y=outer[1][1];

    var inner_tl_x=inner[0][0];
    var inner_tl_y=inner[0][1];

    var inner_br_x=inner[1][0];
    var inner_br_y=inner[1][1];

    return outer_tl_x<inner_tl_x && outer_tl_y<inner_tl_y && outer_br_x>inner_br_x && outer_br_y>inner_br_y;
}

function bounding_box_overlaps(a,b){
   var a_tl_x=a[0][0];
   var a_tl_y=a[0][1];

   var a_br_x=a[1][0];
   var a_br_y=a[1][1];

   var b_tl_x=b[0][0];
   var b_tl_y=b[0][1];

   var b_br_x=b[1][0];
   var b_br_y=b[1][1];

   if(a_tl_x>b_br_x || a_br_x<b_tl_x || a_tl_y>b_br_y || a_br_y<b_tl_y){
      return false;
   }
   else {
      return true;
   }
}

function bounding_box_make(s){
   var minx=Number.MAX_VALUE;
   var miny=Number.MAX_VALUE;
   var maxx=Number.MIN_VALUE;
   var maxy=Number.MIN_VALUE;

   var index;

   for(index=0;index<s.length;++index){
      x=s[index][0];
      y=s[index][1];

      if(x<minx){
         minx=x;
      }
      if(y<miny){
         miny=y;
      }
      if(x>maxx){
         maxx=x;
      }
      if(y>maxy){
         maxy=y;
      }
   }

   return [[minx,miny],[maxx,maxy]]
}

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
         sec.push({'len':acc.length,'resampled':resample(acc,nsample)});
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
      sec.push({'len':acc.length,'resampled':resample(acc,nsample)});
   }

   return {'sec':sec,'len':uniq_points.length}
}

