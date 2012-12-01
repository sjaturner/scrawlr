phantom.injectJs('engine.js');
phantom.injectJs('strokes_append.js');
phantom.injectJs('differences.js');
that={
   strokes:[],
   letters:[]
};
points=[[10,10],[20,20],[30,30]];
strokes_append(that,{stroke:points,bbox:bounding_box_make(points)});

// console.log(JSON.stringify(that));

points=[[410, 113], [410, 112], [411, 112], [412, 112], [413, 112], [416, 112], [421, 112], [432, 112], [447, 112], [462, 112], [480, 111], [499, 110], [518, 109], [534, 108], [547, 108], [557, 108], [562, 108], [566, 108], [567, 108], [566, 108], [565, 108], [564, 108], [563, 108], [562, 109], [559, 110], [551, 112], [535, 117], [508, 127], [490, 133], [475, 140], [453, 147], [420, 159], [406, 165], [398, 168], [393, 170], [389, 172], [390, 172], [394, 171], [401, 170], [432, 166], [469, 162], [507, 157], [547, 153], [585, 149], [613, 147], [628, 145], [639, 145], [644, 145], [646, 145], [645, 145], [645, 145]]
strokes_append(that,{stroke:points,bbox:bounding_box_make(points)});

// console.log(JSON.stringify(that));

phantom.exit(0);
