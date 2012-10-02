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

   while(a.length<64){
      d=[]
      for(i=0;i<a.length;++i){
         d.push(a[i]);
         d.push(a[i]);
      }
      a=d;
   }

   /* incomplete */

   return a;
}

function mean(a){
   var i=0;
   var sum=0;

   for(i=0;i<a.length;++i){
      sum+=a[i];
   }

   return sum/a.length;
}

/*
   console.log(bucket([1,2,9,4,5,6],5,middle));

   function test_deltafun(a,b){
      return a-b;
   }

   console.log(correlate([1,3,4],[2,4,4],test_deltafun))

console.log(resample([1,2,3],10));


phantom.exit();
*/
