phantom.injectJs('angles.js');
phantom.injectJs('utils.js');
function differences_stroke(a,b){
   var ret=[];
   var len_a=a.sec.length;
   var len_b=b.sec.length;
   var most;
   var len_most;
   var most_total_len;
   var least;
   var len_least;
   var least_total_len;
   var offset;
   var log_hi;
   var log_lo;
   var acc_most_len;
   var acc_least_len;
   var scan;
   var score;

   var most_len;
   var least_len;

   var lograt;

   if(len_a>len_b){
      most=a;
      len_most=len_a;

      least=b;
      len_least=len_b;
   }
   else{
      most=b;
      len_most=len_b;

      least=a;
      len_least=len_a;
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
         score=correlate(most.sec[offset+scan].resampled,least.sec[offset].resampled,poldiff);
         console.log(offset+scan,scan,score);
         acc_score+=score;

         most_len=most.sec[offset+scan].len;
         acc_most_len+=most_len;

         least_len=least.sec[scan].len;
         acc_least_len+=least_len;

         lograt=Math.log(most_len/least_len);

         if(lograt>log_hi){
            log_hi=lograt;
         }

         if(lograt<log_lo){
            log_lo=lograt;
         }
      }

      logscale=log_hi-log_lo;
      leastrat=acc_least_len/(1+least_total_len);
      mostrat=acc_most_len/(1+most_total_len);

      if(leastrat==0 || mostrat==0){
         final_score=Number.MAX_VALUE; /* wtf, this cannot happen */
      }
      else{
         final_score=(1+logscale)*acc_score/Math.pow(leastrat*mostrat,3);
      }

      ret.push(final_score);
   }

   return ret;
}

// http://stackoverflow.com/questions/9960908/permutations-in-javascript
// http://jsfiddle.net/MgmMg/6/

/*
 *   Permutate the elements in the specified array by swapping them
 *   in-place and calling the specified callback function on the array
 *   for each permutation.
 *
 *   Return the number of permutations.
 *
 *   If array is undefined, null or empty, return 0.
 *
 *   NOTE: when permutation succeeds, the array should be in the original state
 *   on exit!
 */

function permutate(array, callback) {
    // Do the actual permuation work on array[], starting at index
    function p(array, index, callback) {
        // Swap elements i1 and i2 in array a[]
        function swap(a, i1, i2) {
            var t = a[i1];
            a[i1] = a[i2];
            a[i2] = t;
        }

        // Are we at the last element of the array?                        
        if (index == array.length - 1) {
            // Nothing more to do - call the callback
            callback(array);
            // We have found a single permutation
            return 1;
        } else {
            // Still work to do.
            // Count the number of permutations to our right
            var count = p(array, index + 1, callback);
            // Swap the element at position index with
            // each element to its right, permutate again,
            // and swap back
            for (var i = index + 1; i < array.length; i++) {
                swap(array, i, index);
                count += p(array, index + 1, callback);
                swap(array, i, index);
            }
            return count;
        }
    }

    // No data? Then no permutations!        
    if (!array || array.length == 0) {
        return 0;
    }

    // Start the permutation    
    return p(array, 0, callback);
}


a={"sec":[{"len":155,"resampled":[0,0,0,0,0,0,-0.03,-0.05,-0.05,-0.05,-0.05,-0.05,-0.06,-0.03,0,0]},{"len":183,"resampled":[2.83,2.88,2.84,2.81,2.79,2.79,2.8,2.76,2.72,2.78,2.82,2.82,2.8,2.79,2.74,2.77]},{"len":256,"resampled":[-0.14,-0.13,-0.12,-0.11,-0.1,-0.11,-0.12,-0.12,-0.11,-0.09,-0.09,-0.1,-0.09,-0.08,-0.10500000000000001,0]}],"len":607}
b={"sec":[{"len":155,"resampled":[0,0,0,0,0,0,-0.03,-0.05,-0.05,-0.05,-0.05,-0.05,-0.06,-0.03,0,0]},{"len":183,"resampled":[2.83,2.88,2.84,2.81,2.79,2.79,2.8,2.76,2.72,2.78,2.82,2.82,2.8,2.79,2.74,2.77]},{"len":256,"resampled":[-0.14,-0.13,-0.12,-0.11,-0.1,-0.11,-0.12,-0.12,-0.11,-0.09,-0.09,-0.1,-0.09,-0.08,-0.10500000000000001,0]}],"len":607}
c={"sec":[{"len":155,"resampled":[0,0,0,0,0,0,-0.03,-0.05,-0.05,-0.05,-0.05,-0.05,-0.06,-0.03,0,0]},{"len":256,"resampled":[-0.14,-0.13,-0.12,-0.11,-0.1,-0.11,-0.12,-0.12,-0.11,-0.09,-0.09,-0.1,-0.09,-0.08,-0.10500000000000001,0]}],"len":607}

console.log(differences_stroke(a,c));
phantom.exit();
