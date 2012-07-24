function intcmp(a,b){
   return a-b;
}

function middle(a){
   var sorted=a.sort(intcmp);

   console.log(a)
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
      l.push(samples[0])
   }

   for(i=0;i<half_gap;++i){
      r.push(samples[samples.length-1])
   }

   extended=l.concat(samples,r);
   
   for(i=0;i<samples.length;++i){
      ret.push(fun(extended.slice(i,i+gap)))
   }

   console.log(ret)
}

bucket([1,2,3,4,5,6],5,middle);

phantom.exit();
