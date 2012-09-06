function contains(outer,inner){
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

function overlaps(a,b){
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

function make(s){
}

console.log(contains([[0,0],[10,10]],[[5,5],[10,10]]))

phantom.exit();
