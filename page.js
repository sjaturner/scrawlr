$(function() {
   var mobile_device = {
       android: function() {
           return navigator.userAgent.match(/Android/i) ? true : false;
       },
       blackberry: function() {
           return navigator.userAgent.match(/BlackBerry/i) ? true : false;
       },
       ios: function() {
           return navigator.userAgent.match(/iPhone|iPad|iPod/i) ? true : false;
       },
       windows: function() {
           return navigator.userAgent.match(/IEMobile/i) ? true : false;
       },
       any: function() {
           return mobile_device.android() || mobile_device.blackberry() || mobile_device.ios() || mobile_device.windows();
       }
   };

	var drawDot = function(context, color, x, y) {
		context.fillStyle = color;
		context.fillRect (x, y, 5, 5);
	}
	
	var canvas = $("#page")[0];
	var context = canvas.getContext("2d");
	
	var mouseclicked = false
	
   function down(e){
		mouseclicked = true;
   }

   function up(e){
		mouseclicked = false;
   }

   function move(e){
		if(mouseclicked === true) {
			var x = e.pageX;
			var y = e.pageY;
			drawDot(context, '#BADA55', x, y);
		};
   }

   if(mobile_device.any()){
      canvas.addEventListener('touchstart',down);
      canvas.addEventListener('touchend',up);
      canvas.addEventListener('touchmove',function (e){
			e.preventDefault();
         move(e);
      });
   }
   else{
      $("#page").mousedown(down);
      $("#page").mouseup(up);
      $("#page").mousemove(move);
   }
});
