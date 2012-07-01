//$(document).ready(function() {
//
//   var a_canvas = $("#a_canvas")[0];
//   var ctx = a_canvas.getContext("2d");
//
//   ctx.fillStyle = "rgb(0,0,255)";
//   ctx.fillRect(50, 25, 150, 100);
//});

$(document).ready(function(){
   var canvas;
   var context; 
   var tool;

   function init(){
      canvas = $('#a_canvas')[0];
      if (!canvas) {
         alert('Error: I cannot find the canvas element!');
         return;
      }

      if (!canvas.getContext) {
         alert('Error: no canvas.getContext!');
         return;
      }

      context = canvas.getContext('2d'); 
      if (!context) {
         alert('Error: failed to getContext!');
         return;
      }

      // Pencil tool instance.
      tool = new pencil();

      // Attach the mousedown, mousemove and mouseup event listeners.
      canvas.addEventListener('mousedown', ev_canvas, false);
      canvas.addEventListener('mousemove', ev_canvas, false);
      canvas.addEventListener('mouseup',   ev_canvas, false);
   }

   function pencil(){
      var tool = this;
      this.started = false;

      // This is called when you start holding down the mouse button.
      // This starts the pencil drawing.
      this.mousedown = function (ev) {
         context.beginPath();
         context.moveTo(ev._x, ev._y);
         tool.started = true;
      };

      // This function is called every time you move the mouse. Obviously, it only 
      // draws if the tool.started state is set to true (when you are holding down 
      // the mouse button).
      this.mousemove = function (ev) {
         if (tool.started) {
            context.lineTo(ev._x, ev._y);
            context.stroke();
         }
      };

      // This is called when you release the mouse button.
      this.mouseup = function (ev) {
         if (tool.started) {
            tool.mousemove(ev);
            tool.started = false;
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

      // Call the event handler of the tool.
      var func = tool[ev.type];
      if (func) {
         func(ev);
      }
   }

   init();
});
