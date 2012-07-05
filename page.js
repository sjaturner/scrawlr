// notes
//    get a local copy of jquery you muppet
//    nice to have phantom js to built test code
//       can probably test harness some of this stuff
//    do simplistic saving of lines and strokes
//    then render to support canvas moves
//    then the bounding box stuff
//    next code up the line points algorithm
//    then bucket median filter stuff
$(document).ready(function(){
   var canvas;
   var ctx; 
   var tool;
   var width=0;
   var height=0;

   var orgx=0;
   var orgy=0;

   function render(){
      var linegap=40;
      var y=0;

      for(y=0;y<height;y+=linegap)
      {
         var oy=(y-orgy%linegap)>>>0;

         ctx.beginPath();
         ctx.moveTo(0,oy);
         ctx.lineTo(width,oy);
         ctx.strokeStyle = "#000001";
         ctx.stroke();
      }
   }

   function init(){
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

      tool=new pen();

      canvas.addEventListener('mousedown', ev_canvas, false);
      canvas.addEventListener('mousemove', ev_canvas, false);
      canvas.addEventListener('mouseup',   ev_canvas, false);

      width=canvas.width;
      height=canvas.height;

      render();
   }

   function pen(){
      var that=this; 
      var dwell_ms_for_move=500;
      var drag=0;
      var draw=0;

      that.mousedown=function(ev){
         var date=new Date();

         ctx.beginPath();
         ctx.moveTo(ev._x, ev._y);

         that.down={}
         that.down['time']=date.getTime();
         that.down['x']=ev._x;
         that.down['y']=ev._y;
      }

      that.mousemove=function(ev){
         if('down' in that){
            if(that['down'].time){
               var date=new Date();
               var time=date.getTime();
               var dwell=time-that['down'].time;

               if(dwell>=dwell_ms_for_move){
                  drag=1;
               }
               else{
                  // need to record start time for stroke
                  draw=1;
               }

               that['down'].time=0;
            }
         }

         if(draw){
            ctx.lineTo(ev._x, ev._y);
            ctx.strokeStyle = "#000000";
            ctx.stroke();
         }

         if(drag){
         }
      }

      that.mouseup=function(ev){
         if('down' in that){
            that.mousemove(ev);

            if(that['down']){ // then there has been no move, do select action instead
            }

            if(drag){ // finish drag 

               drag=0;
            }
            
            if(draw){ // finish draw

               draw=0;
            }

            delete that['down'];
         }
         
      }
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

   init();
});
