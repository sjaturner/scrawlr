function differences_stroke(a,b){
   var ret=[];
   var len_a=a.sec;
   var len_b=b.sec;
   var most;
   var most_len;
   var most_total_len;
   var least;
   var least_len;
   var least_total_len;
   var offset;
   var log_hi;
   var log_lo;
   var acc_most_len;
   var acc_least_len;
   var scan;

   if(len_a>len_b){
      most=a;
      most_len=len_a;

      least=b;
      least_len=len_b;
   }
   else{
      most=b;
      most_len=len_b;

      least=a;
      least_len=len_a;
   }

   most_total_len=most.len;
   least_total_len=least.len;

   for(offset=0;offset<len_most-len_least+1;++offset){
      log_hi=Number.MIN_VALUE;
      log_lo=Number.MAX_VALUE;
      acc_most_len=0;
      acc_least_len=0;
      acc_score=0;

      for(scan=0;scan<len_least;++scan){
      }
   }

   return ret;
}
