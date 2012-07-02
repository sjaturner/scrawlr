$(document).ready(function(){
   var canvas;
   var ctx; 
   var tool;
   var width=0;
   var height=0;
   var update=0;

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
      var tool=this; 
      this.started=false;

      tool.mousedown=function(ev){
         ctx.beginPath();
         ctx.moveTo(ev._x, ev._y);
         tool.started=true;
      };

      tool.mousemove=function(ev){
         if(tool.started){
            ctx.lineTo(ev._x, ev._y);
            ctx.strokeStyle = "#000000";
            ctx.stroke();
         }
      };

      tool.mouseup=function(ev){
         if(tool.started){
            tool.mousemove(ev);
            tool.started=false;
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

   init();
});
