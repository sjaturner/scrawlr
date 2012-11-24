var page = require('webpage').create();
page.viewportSize = { width: 1024, height : 640 };
page.content = '<html><body><canvas id="surface" width=1024 height=640></canvas></body></html>';
page.evaluate(function() {
   var a={"sec": [{"resampled": [-1.9600000000000002, -2.77, -2.9350000000000001, -3.105, -3.3300000000000001, -3.5649999999999999, -3.7549999999999999, -4.1500000000000004, -4.8249999999999993, -5.4779999999999998, -6.4800000000000004, -6.6850000000000005, -6.8099999999999996, -6.8799999999999999, -6.9850000000000003, -7.2499999999999973], "len": 257}, {"resampled": [-4.7607692307692311, -5.0800000000000001, -4.9450000000000003, -4.9649999999999999, -5.0199999999999996, -4.9900000000000002, -4.96, -4.9500000000000002, -4.9500000000000002, -4.9500000000000002, -4.9500000000000002, -4.9500000000000002, -4.8949999999999996, -4.8849999999999998, -5.0650000000000004, -5.1000000000000005], "len": 57}], "len": 319}
   var el = document.getElementById('surface');
   var ctx = el.getContext('2d');
   var width = window.innerWidth;
   var xo=width/2;
   var height = window.innerHeight
   var yo=height/2;

   var colour=['#ffff00','#ff00ff','#00ffff']

   function draw_sections(ctx,sec,scale_noise,rotate_noise,scale,rotate){
      var i=0;
      var xx=xo;
      var yy=yo;

      for(i=0;i<sec.length;++i){
         var len=sec[i].len;
         var seg=sec[i].resampled;
         var j=0;

         ctx.beginPath();
         ctx.moveTo(xx,yy);

         for(j=0;j<seg.length;++j){
            var theta=seg[j]+rotate+(Math.random()-0.5)*rotate_noise;
            var mag=scale*Math.abs(len/seg.length*(1+(Math.random()-0.5)*scale_noise));

            xx+=mag*Math.cos(theta);
            yy+=mag*Math.sin(theta);

            ctx.lineTo(xx,yy);
         }

         ctx.strokeStyle = colour[i%colour.length];
         ctx.stroke();
      }
   }

   draw_sections(ctx,a.sec,0,0.5,(1+0.5*(Math.random()-0.5)),0.2*(Math.random()-0.5));

   document.body.style.backgroundColor = 'white';
   document.body.style.margin = '0px';
});

page.render('colorwheel.png');

phantom.exit();

// scale noise
// rotate noise
// rotate
