var page = require('webpage').create();
page.viewportSize = { width: 400, height : 400 };
page.content = '<html><body><canvas id="surface"></canvas></body></html>';
page.evaluate(function() {
   var a={"sec": [{"resampled": [-1.9600000000000002, -2.77, -2.9350000000000001, -3.105, -3.3300000000000001, -3.5649999999999999, -3.7549999999999999, -4.1500000000000004, -4.8249999999999993, -5.4779999999999998, -6.4800000000000004, -6.6850000000000005, -6.8099999999999996, -6.8799999999999999, -6.9850000000000003, -7.2499999999999973], "len": 257}, {"resampled": [-4.7607692307692311, -5.0800000000000001, -4.9450000000000003, -4.9649999999999999, -5.0199999999999996, -4.9900000000000002, -4.96, -4.9500000000000002, -4.9500000000000002, -4.9500000000000002, -4.9500000000000002, -4.9500000000000002, -4.8949999999999996, -4.8849999999999998, -5.0650000000000004, -5.1000000000000005], "len": 57}], "len": 319}
   var el = document.getElementById('surface');
   var ctx = el.getContext('2d');
   var width = window.innerWidth;
   var xo=width/2;
   var height = window.innerHeight
   var yo=height/2;

   console.log('here');

   function draw_sections(ctx,sec){
      var i=0;
      var x=100;
      var y=100;

      for(i=0;i<sec.length;++i){
         var len=sec[i].len;
         var seg=sec[i].resampled;
         var j=0;

         ctx.beginPath();
         ctx.moveTo(x,y);

         for(j=0;j<seg.length;++j){
            var theta=seg[j];

            x+=Math.sin(theta)*len;
            y+=Math.cos(theta)*len;
            ctx.lineTo(x,y);
         }

         ctx.strokeStyle = "#000000";
         ctx.stroke();
      }

      if(1){
         ctx.beginPath();
         ctx.moveTo(10,10);
         ctx.lineTo(20,20);
         ctx.strokeStyle = "#000000";
         ctx.stroke();
      }
   }

   draw_sections(ctx,a.sec);

   document.body.style.backgroundColor = 'white';
   document.body.style.margin = '0px';
});

page.render('colorwheel.png');
console.log('done');

phantom.exit();
