// notes
//    get a local copy of jquery you muppet (done)
//    nice to have phantom js to built test code (done)
//       can probably test harness some of this stuff
//    do simplistic saving of lines and strokes
//    then render to support canvas moves
//    then the bounding box stuff
//    next code up the line points algorithm
//    then bucket median filter stuff
$(document).ready(function(){

   function paper(){
      var that=this;
      var paper_this=this;
      var canvas;
      var ctx; 
      var tool;
      var width=0;
      var height=0;

      this.orgx=0;
      this.orgy=0;
      var current_stroke=null;
      var dorg=null;

      that.strokes=[];
      that.letters=[];
      that.focus=null;


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

      function bounding_box_extend(bbox,s){
         var minx=bbox[0][0];
         var miny=bbox[0][1];
         var maxx=bbox[1][0];
         var maxy=bbox[1][1];

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

      function bounding_box_make(s){
         var minx=Number.MAX_VALUE;
         var miny=Number.MAX_VALUE;
         var maxx=Number.MIN_VALUE;
         var maxy=Number.MIN_VALUE;

         return bounding_box_extend([[Number.MAX_VALUE,Number.MAX_VALUE],[Number.MIN_VALUE,Number.MIN_VALUE]],s);
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
               score=correlate(most.sec[offset+scan].resampled,least.sec[scan].resampled,poldiff);
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

      function differences_multipart(a,b){
         var ret=[];
         var perms=[];
         var pi;
         var score;
         var bi;
         var res;

         permutate(a,function(p){
            perms.push(p.slice(0));
         });

         for(pi=0;pi<perms.length;++pi){
            score=0;
            for(bi=0;bi<b.length;++bi){
               score+=differences_stroke(perms[pi][bi],b[bi]).sort(intcmp)[0];
            }
            ret.push(score);
         }

         return ret;
      }

      function score_sort(a,b){
         return -a[0]+b[0];
      }

      function differences_multipart_shim(that,stroke_indexes_a,stroke_indexes_b){
         var stroke_array_a=[];
         var stroke_array_b=[];
         var i=0;

         for(i=0;i<stroke_indexes_a.length;++i){
            stroke_array_a.push(that.strokes[stroke_indexes_a[i]]);
         }

         for(i=0;i<stroke_indexes_b.length;++i){
            stroke_array_b.push(that.strokes[stroke_indexes_b[i]]);
         }

         return differences_multipart(stroke_array_a,stroke_array_b);
      }

      function strokes_append(that,stroke){
         var val=salient(stroke.stroke);
         var multipart_letter=null;
         var multipart_letter_index=-1;
         var i=0;
         var stroke_point_set=null;
         var multipart_letter_len=0;
         var letter_index=0;
         var letter=null;
         var score_index=0;
         var differences=[];
         var score_table=[];
         var score=0;
         var item=[];
         var new_stroke_index=that.strokes.length;

         stroke.time=(new Date).getTime();
         stroke.sec=val.sec;
         stroke.len=val.len;
         stroke.bbox=bounding_box_make(stroke.stroke);

         that.strokes.push(stroke);

         for(i=0;i<that.strokes.length;++i){
            if(that.strokes[i].stroke==stroke){
               continue;
            }

            if(bounding_box_overlaps(stroke.bbox,that.strokes[i].bbox)){

               if(stroke_point_set==null){
                  stroke_point_set=stroke_to_point_set(stroke.stroke);
               }

               if(intersects(stroke_point_set,stroke_to_point_set(that.strokes[i].stroke))){
                  multipart_letter_index=that.strokes[i].letter_index;
                  break;
               }
            }
         }

         if(multipart_letter_index>=0){
            multipart_letter=that.letters[multipart_letter_index];
            multipart_letter.item.push(new_stroke_index);
            multipart_letter.bbox=bounding_box_extend(multipart_letter.bbox,stroke.stroke);

            stroke.letter_index=multipart_letter_index;
            that.focus=multipart_letter;;
            multipart_letter_len=multipart_letter.item.length;

            for(letter_index=0;letter_index<that.letters.length;++letter_index){
               letter=that.letters[letter_index];
               if(letter_index==multipart_letter_index){
                  continue;
               }
               else if(letter.item.length!=multipart_letter_len){
                  continue;
               }
               else
               {
                  differences=differences_multipart_shim(that,multipart_letter.item,letter.item);

                  for(score_index=0;score_index<differences.length;++score_index){
                     score_table.push([differences[score_index],letter]);
                  }
               }
            }

            score_table=score_table.sort(score_sort);

            for(score_index=0;score_index<score_table.length;++score_index){
               score=score_table[score_index][0];
               letter=score_table[score_index][1];

               if(letter.hasOwnProperty('char') && letter.char.hasOwnProperty('type') && letter.char.type=='told'){
                  multipart_letter.char={'type':'guess','val':letter.char.val};
               }
            }

            if(multipart_letter.hasOwnProperty('char')){
               console.log('multipart',String.fromCharCode(multipart_letter.char.val));
            }
         }
         else{
            var new_letter={};

            for(letter_index=0;letter_index<that.letters.length;++letter_index){
               letter=that.letters[letter_index];

               if(letter.item.length==1){
                  var stroke_index=letter.item[0];

                  differences=differences_stroke(stroke,that.strokes[stroke_index]);
                  for(score_index=0;score_index<differences.length;++score_index){
                     score_table.push([differences[score_index],letter]);
                  }
               }
            }

            score_table=score_table.sort(score_sort);

            new_letter.item=[new_stroke_index];
            new_letter.bbox=stroke.bbox;

            for(i=0;i<score_table.length;++i){
               score=score_table[i][0];
               letter=score_table[i][1];

               if(letter.hasOwnProperty('char') && letter.char.hasOwnProperty('type') && letter.char.type=='told'){
                  new_letter.char={'type':'guess','val':letter.char.val};
               }
            }

            if(new_letter.hasOwnProperty('char')){
               console.log('onepart',String.fromCharCode(new_letter.char.val));
            }

            stroke.letter_index=that.letters.length;
            that.focus=new_letter;

            that.letters.push(new_letter);
         }

         console.log(JSON.stringify(that.letters));
         console.log(JSON.stringify(that.strokes));
      }

      function focus_letter(that,x,y){
         var letter_index=0;
         var point_bbox=[[x-1,y-1],[x+1,y+1]];

         for(letter_index=0;letter_index<that.letters.length;++letter_index){ 
            var letter=that.letters[letter_index]; 
            var stroke_index=0;

            for(stroke_index=0;stroke_index<letter.item.length;++stroke_index){
               if(bounding_box_overlaps(letter.item[stroke_index].bbox,point_bbox)){
                  return letter;
               }
            }
         }
         return null;
      }

      function stroke_in_focus(stroke,focus){
         var i=0;

         if(!focus){
            return false;
         }
  
         for(i=0;i<focus.item.length;++i){
            if(focus.item[i].stroke==stroke){
               return true;
            }
         }

         return false;
      }

      function render(){
         var linegap=40;
         var y=0;
         var focus="#ff0000";
         var black="#000000";
         var colour="";

         function stroke_render(stroke,colour){
            if(stroke.length<2){
               return;
            }

            ctx.beginPath();
            for(var i=0;i<stroke.length;++i){
               var x=stroke[i][0]-that.orgx;
               var y=stroke[i][1]-that.orgy;

               if(i){
                  ctx.lineTo(x,y);
               }
               else{
                  ctx.moveTo(x,y);
               }
            }
            ctx.strokeStyle = colour;
            ctx.stroke();
         }

         canvas.width = canvas.width;

         for(y=0;y<height;y+=linegap)
         {
            var oy=(y-that.orgy%linegap)>>>0;

            ctx.beginPath();
            ctx.moveTo(0,oy);
            ctx.lineTo(width,oy);
            ctx.strokeStyle = "#000001";
            ctx.stroke();
         }

         for(var i=0;i<that.strokes.length;++i){
            var this_stroke=that.strokes[i];

            stroke_render(this_stroke.stroke,stroke_in_focus(that.strokes[i].stroke,that.focus)?focus:black);

            if(this_stroke.hasOwnProperty('letter_index')){
               var the_letter=that.letters[this_stroke.letter_index];

               if(the_letter.hasOwnProperty('bbox')){
                  var letter=the_letter;
                  var bbox=letter.bbox;
                  var minx=bbox[0][0]-that.orgx;
                  var miny=bbox[0][1]-that.orgy;
                  var maxx=bbox[1][0]-that.orgx;
                  var maxy=bbox[1][1]-that.orgy;

                  ctx.beginPath();
                  ctx.moveTo(minx,miny);
                  ctx.lineTo(minx,maxy);
                  ctx.lineTo(maxx,maxy);
                  ctx.lineTo(maxx,miny);
                  ctx.lineTo(minx,miny);
                  ctx.strokeStyle = "#808080";
                  ctx.stroke();
                  if(letter.hasOwnProperty('char')){
                     if(letter.char.type=='told'){
                        ctx.strokeStyle = 'green';
                     }
                     else{
                        ctx.strokeStyle = 'blue';
                     }

                     ctx.strokeText(String.fromCharCode(letter.char.val),minx,miny);
                  }
                  else{
                     ctx.strokeText('?',minx,miny);
                  }
               }
            }
         }

         if(current_stroke){
            stroke_render(current_stroke,stroke_in_focus(current_stroke,that.focus)?focus:black);
         }
      }

      document.onkeydown=function(event){ /* this is so crap, fix it */
         var code;
         if('which' in event){
            code=event.which;
            if('shiftKey' in event){
               if(code==16){
                  return;
               }
               if(event.shiftKey){
               }
               else{
                  code+=32;
               }
            }
         }
         else{
            code=event.keyCode;
            if('shiftKey' in event){
               if(code==16){
                  return;
               }
               if(event.shiftKey){
               }
               else{
                  code+=32;
               }
            }
         }

         paper_this.focus.char={'type':'told','val':code};
         render();
      }

      function handle_mouseout(ev){
         console.log('mouseout');

         var frm = $(document.myform);
         var dat = JSON.stringify({
            'orgx':that.orgx,
            'orgy':that.orgy,
            'strokes':that.strokes,
            'letters':that.letters
         },
         function(key, val) {
             return val.toFixed ? Number(val.toFixed(3)) : val;
         }); 

         that.focus=that.strokes[that.strokes.length-1];

         $.post(
            "/json",
            dat,
            function(data) {
            }
         );
      }

      this.init=function(){
         canvas=$('#a_canvas')[0];
         if(!canvas){
            alert('no canvas element');
            return;
         }

         if(!canvas.getContext){
            alert('no canvas.getContext!');
            return;
         }

         ctx=canvas.getContext('2d'); 
         if(!ctx){
            alert('cannot get ctx');
            return;
         }

         ctx.lineWidth=1;

         tool=new pen(this);

         canvas.addEventListener('mousedown', ev_canvas, false);
         canvas.addEventListener('mousemove', ev_canvas, false);
         canvas.addEventListener('mouseup',   ev_canvas, false);
         canvas.addEventListener('mouseout',  handle_mouseout, false);

         width=canvas.width;
         height=canvas.height;

         $.get('json', function(str) {
            var data=JSON.parse(str);

            if(data=={}){
               return;
            }
            console.log(data);
            that.orgx=data.orgx;
            that.orgy=data.orgy;
            that.strokes=data.strokes;
            that.letters=data.letters;
            render();
         });
      };

      function pen(paper){
         var that=this; 
         var dwell_ms_for_move=500;
         var drag=0;
         var draw=0;


         that.mousedown=function(ev){
            var date=new Date();

            that.down={};
            that.down.time=date.getTime();
            that.down.x=ev._x;
            that.down.y=ev._y;
            that.down.drag=ev.which==2;
         };

         that.mousemove=function(ev){
            var first=0;

            if('down' in that){
               if(that.down.time){
                  first=1;

                  that.dloc=[ev._x, ev._y];
                  if(that.down.drag){
                     that.dorg=[ev._x, ev._y];
                     drag=1;
                  }
                  else{
                     var date=new Date();
                     var time=date.getTime();
                     var dwell=time-that.down.time;

                     if(dwell>=dwell_ms_for_move){
                        that.dorg=[ev._x, ev._y];
                        drag=1;
                     }
                     else{
                        // need to record start time for stroke
                        draw=1;
                     }
                  }

                  that.down.time=0;
               }
            }

            if(draw){
               if(first){
                  ctx.beginPath();
                  ctx.moveTo(ev._x, ev._y);
                  that.current_stroke=[];
                  first=0;
               }
               else{
                  ctx.lineTo(ev._x, ev._y);
               }
               that.current_stroke.push([ev._x+paper.orgx, ev._y+paper.orgy]);

               ctx.strokeStyle = "#000001";
               ctx.stroke();
            }

            if(drag){
               var x=that.dorg[0]-ev._x;
               var y=that.dorg[1]-ev._y;

               paper.orgx+=x;
               paper.orgy+=y;

               that.dorg=[ev._x, ev._y];
               render();
            }
         };

         that.mouseup=function(ev){
            if('down' in that){
               that.mousemove(ev);

               if(drag){ 
                  var x=that.dorg[0]-ev._x;
                  var y=that.dorg[1]-ev._y;
                  var xdloc=that.dloc[0];
                  var ydloc=that.dloc[1];
                  var dx=ev._x-xdloc;
                  var dy=ev._y-ydloc;
                  var r=Math.sqrt(dx*dx+dy*dy);

                  if(r<5){
                     paper_this.focus=focus_letter(paper_this,ev._x+paper.orgx, ev._y+paper.orgy);
                  }
                  
                  paper.orgx+=x;
                  paper.orgy+=y;

                  that.dorg=[ev._x, ev._y];
                  render();
                  drag=0;
                  that.dorg=null;
               }
               
               if(draw){ // finish draw
                  strokes_append(paper_this,{'stroke':that.current_stroke,})
                  render();

                  that.current_stroke=null;
                  draw=0;
               }

               delete that.down;
            }
         };
      }

      function ev_canvas(ev){
         var x=new Number();
         var y=new Number();

         if (event.x!=undefined && event.y!=undefined){
            x=event.x;
            y=event.y;
         }
         else{
            x=event.clientX+document.body.scrollLeft+document.documentElement.scrollLeft;
            y=event.clientY+document.body.scrollTop+document.documentElement.scrollTop;
         }

         x-=canvas.offsetLeft;
         y-=canvas.offsetTop;

         ev._x=x;
         ev._y=y;

         var func=tool[ev.type];
         if(func){
            func(ev);
         }
      }
   }

   var handle=new paper();

   handle.init();
});
