function strokes_append(that,stroke){
   var val=salient(stroke.stroke);
   var multipart_letter=null;
   var i=0;
   var stroke_point_set={}; 
   var multipart_letter_len=0;
   var letter_index=0;
   var letter=null;
   var score_index=0;
   var differences=[];
   var score_table=[];
   var score=0;
   var item=[];

   stroke.time=(new Date).getTime();

   if(1){
      for(i=0;i<that.strokes.length;++i){
         if(bounding_box_overlaps(stroke.bbox,that.strokes[i].bbox)){
            if(!stroke_point_set){
               stroke_to_point_set=stroke_to_point_set(stroke.stroke);
            }

            if(intersects(stroke_point_set,stroke_to_point_set(that.strokes[i].stroke))){
               multipart_letter=that.strokes[i].letter;
               break;
               /* contact */
            }
         }
      }

      if(multipart_letter){
         multipart_letter.item.push(stroke);
         stroke.letter=multipart_letter;
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
                  score_table.push([differences[score_index],0,letter]);
               }
            }
         }

         score_table=score_table.sort();

         for(score_index=0;score_index<score_table.length;++score_index){
            score=score_table[score_index][0];
            /* index one is degenerate */
            letter=score_table[score_index][2];

            if(letter.hasOwnProperty('char') && letter.char.hasOwnProperty('type') && letter.char.type=='told'){
               console.log('#',score,letter.char.val);

               multipart_letter.char={'type':'guess','val':letter.char.val};
            }
         }
      }
      else{
         for(letter_index=0;letter_index<that.letters.length;++letter_index){
            letter=that.letters[letter_index];
            item=letter.item[0];

            differences=differences_stroke(stroke,item);
            for(score_index=0;score_index<differences.length;++score_index){
               score_table.push([differences[score_index],item,letter]);
            }
         }
      }
   }

   stroke.sec=val.sec;
   stroke.len=val.len;

   console.log(that);
   console.log(that.strokes);
   that.strokes.push(stroke);
}
