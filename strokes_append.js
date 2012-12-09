function score_sort(a,b){
   return -a[0]+b[0];
}

function strokes_append(that,stroke){
   var val=salient(stroke.stroke);
   var multipart_letter=null;
   var i=0;
   var stroke_point_set=null;
   var multipart_letter_len=0;
   var letter_index=0;
   var letter=null;
   var score_index=0;
   var differences=[];
   var score_table=[];
   var score=0;
   var item=[];

   stroke.time=(new Date).getTime();
   stroke.sec=val.sec;
   stroke.len=val.len;
   stroke.bbox=bounding_box_make(stroke.stroke);

   for(i=0;i<that.strokes.length;++i){
      if(bounding_box_overlaps(stroke.bbox,that.strokes[i].bbox)){

         if(stroke_point_set==null){
            stroke_point_set=stroke_to_point_set(stroke.stroke);
         }

         if(intersects(stroke_point_set,stroke_to_point_set(that.strokes[i].stroke))){
            multipart_letter=that.strokes[i].letter;
            break;
         }
      }
   }

   if(multipart_letter){
      multipart_letter.item.push(stroke);
      multipart_letter.bbox=bounding_box_extend(multipart_letter.bbox,stroke);

      stroke.letter=multipart_letter;
      that.focus=multipart_letter;;
      multipart_letter_len=multipart_letter.item.length;

      for(letter_index=0;letter_index<that.letters.length;++letter_index){
         letter=that.letters[letter_index];
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
               score_table.push([differences[score_index],letter]);
            }
         }
      }

      score_table=score_table.sort(score_sort);

      for(score_index=0;score_index<score_table.length;++score_index){
         score=score_table[score_index][0];
         letter=score_table[score_index][1];

         if(letter.hasOwnProperty('char') && letter.char.hasOwnProperty('type') && letter.char.type=='told'){
            multipart_letter.char={'type':'guess','val':letter.char.val};
         }
      }

      if(multipart_letter.hasOwnProperty('char')){
         console.log('multipart',String.fromCharCode(multipart_letter.char.val));
      }
   }
   else{
      var new_letter={};

      for(letter_index=0;letter_index<that.letters.length;++letter_index){
         letter=that.letters[letter_index];
         item=letter.item[0];

         if(letter.item.length!=1){
            continue;
         }

         differences=differences_stroke(stroke,item);
         for(score_index=0;score_index<differences.length;++score_index){
            score_table.push([differences[score_index],letter]);
         }
      }

      score_table=score_table.sort(score_sort);

      new_letter.item=[stroke];
      new_letter.bbox=stroke.bbox;

      for(i=0;i<score_table.length;++i){
         score=score_table[i][0];
         letter=score_table[i][1];

         if(letter.hasOwnProperty('char') && letter.char.hasOwnProperty('type') && letter.char.type=='told'){
            new_letter.char={'type':'guess','val':letter.char.val};
         }
      }

      if(new_letter.hasOwnProperty('char')){
         console.log('onepart',String.fromCharCode(new_letter.char.val));
      }

      stroke.letter=new_letter;
      that.focus=new_letter;

      that.letters.push(new_letter);
   }

   that.strokes.push(stroke);
}

function focus_letter(that,x,y){
   var letter_index=0;
   var point_bbox=[[x-1,y-1],[x+1,y+1]];

   for(letter_index=0;letter_index<that.letters.length;++letter_index){
      var letter=that.letters[letter_index];
      var stroke_index=0;
      for(stroke_index=0;stroke_index<letter.item.length;++stroke_index){
         if(bounding_box_overlaps(letter.item[stroke_index].bbox,point_bbox)){
            return letter;
         }
      }
   }
   return null;
}
