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

      /* #include "engine.js" */
      /* #include "strokes_append.js" */

      function stroke_in_focus(stroke,focus){
         var i=0;
  
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

            if(this_stroke.hasOwnProperty('letter')){
               if(this_stroke.letter.hasOwnProperty('bbox')){
                  var bbox=this_stroke.letter.bbox;
                  var minx=bbox[0][0];
                  var miny=bbox[0][1];
                  var maxx=bbox[1][0];
                  var maxy=bbox[1][1];

                  ctx.beginPath();
                  ctx.moveTo(minx,miny);
                  ctx.lineTo(minx,maxy);
                  ctx.lineTo(maxx,maxy);
                  ctx.lineTo(maxx,miny);
                  ctx.lineTo(minx,miny);
                  ctx.strokeStyle = "#808080";
                  ctx.stroke();
               }
            }
         }

         if(current_stroke){
            stroke_render(current_stroke,stroke_in_focus(current_stroke,that.focus)?focus:black);
         }
      }

      document.onkeydown=function(event){
         var code=('which' in event)?event.which:event.keyCode;
         paper_this.focus.char={'type':'told','val':code};
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
