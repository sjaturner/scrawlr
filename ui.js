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
      var canvas;
      var ctx; 
      var tool;
      var width=0;
      var height=0;

      this.orgx=0;
      this.orgy=0;
      var current_stroke=null;
      var dorg=null;
      this.strokes=[];

      /* #include "engine.js" */

      function strokes_append(stroke){
         var val=salient(stroke.stroke);
         var multipart_letter=null;
         var i=0;
         var stroke_point_set={}; 
         var multipart_letter_len=0;
         var letter_index=0;
         var letter=null;
         var score_index=0;
         var differences=[];
         var score_table=[];
         var score=0;
         var item=[];

         stroke.time=(new Date).getTime();

         for(i=0;i<that.strokes.length;++i){
            if(bounding_box_overlaps(stroke.bbox,strokes[i].bbox)){
               if(!stroke_point_set){
                  stroke_to_point_set=stroke_to_point_set(stroke.stroke);
               }

               if(intersects(stroke_point_set,stroke_to_point_set(strokes[i].stroke)))){
                  multipart_letter=strokes[i].letter;
                  break;
                  /* contact */
               }
            }
         }

         if(multipart_letter){
            multipart_letter.item.push(stroke);
            stroke.letter=multipart_letter;
            multipart_letter_len=multipart_letter.item.length;

            for(letter_index=0;letter_index<letters.length;++letter_index){
               letter=letters[letter_index];
               if(letter==multipart_letter){
                  continue;
               }
               else if(letter.item.length!=multipart_letter_len){
                  continue;
               }
               else
               {
                  differences=differences_multipart(multipart_letter.item,letter.item);

                  for(score_index=0;score_index<differences.length;++score_index){
                     score_table.push([differences[score_index],0,letter]);
                  }
               }
            }

            score_table=score_table.sort();

            for(score_index=0;score_index<score_table.length;++score_index){
               score=score_table[score_index][0];
               /* index one is degenerate */
               letter=score_table[score_index][2];

               if(letter.hasOwnProperty('char') && letter.char.hasOwnProperty('type') && letter.char.type=='told'){
                  console.log('#',score,letter.char.val);

                  multipart_letter.char={'type':'guess','val':letter.char.val};
               }
            }
         }
         else{
            for(letter_index=0;letter_index<letters.length;++letter_index){
               letter=letters[letter_index];
               item=letter.item[0];

               differences=differences_stroke(stroke,item);
               for(score_index=0;score_index<differences.length;++score_index){
                  score_table.push([differences[score_index],item,letter]);
               }
            }
         }

         console.log(val);

         /* 
         if(!val){
            console.log('fail');
            return;
         }
         else[
            console.log('here');
         }
         
         stroke.sec=val.sec;
         stroke.len=val.len;
         */

         that.strokes.push(stroke);
      }

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
         ctx.strokeStyle = "#000000";
         ctx.stroke();
      }

      function render(){
         var linegap=40;
         var y=0;

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
            stroke_render(that.strokes[i].stroke,0);
         }

         if(current_stroke){
            stroke_render(current_stroke,0);
         }
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

         width=canvas.width;
         height=canvas.height;

         render();
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

               ctx.strokeStyle = "#000000";
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

               if(drag){ // finish drag 
                  var x=that.dorg[0]-ev._x;
                  var y=that.dorg[1]-ev._y;

                  paper.orgx+=x;
                  paper.orgy+=y;


                  that.dorg=[ev._x, ev._y];
                  render();
                  drag=0;
                  that.dorg=null;
               }
               
               if(draw){ // finish draw
                  strokes_append({'stroke':that.current_stroke,'bbox':bounding_box_make(that.current_stroke)})

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
