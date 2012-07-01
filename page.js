$(document).ready(function(){
   var canvas;
   var context; 
   var tool;

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

      context=canvas.getContext('2d'); 
      if(!context){
         alert('cannot get context');
         return;
      }

      tool=new pen();

      canvas.addEventListener('mousedown', ev_canvas, false);
      canvas.addEventListener('mousemove', ev_canvas, false);
      canvas.addEventListener('mouseup',   ev_canvas, false);
   }

   function pen(){
      var tool=this;
      this.started=false;

      this.mousedown=function(ev){
         context.beginPath();
         context.moveTo(ev._x, ev._y);
         tool.started=true;
      };

      this.mousemove=function(ev){
         if(tool.started){
            context.lineTo(ev._x, ev._y);
            context.stroke();
         }
      };

      this.mouseup=function(ev){
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
