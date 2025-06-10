path_to_stl = "C:/Users/38066/Downloads/map_tiles/stl/krim.stl";

inner_h = 12;
outer_h = 16;
thickness = 4;

strip_h = 10;
strip_depth = 2;

// Модуль для імпорту оригінальної частини
module original_part(){
    color("green", 0.7){
        scale([0.4,0.4,0.4]){
        import(path_to_stl);
    }}
}

// Модуль для вирізання частини
module cut_part(){
    color("red"){
        translate([0, 0, outer_h-inner_h]){
            linear_extrude(height = strip_h){
                offset(r=-strip_depth, chamfer = true){
                    projection(cut = true){
                        original_part();
                    }
                }
            }
        }
    }
}

// Модуль для заокруглення країв
module rounding(){
    color("blue"){
        union(){
            start_h = outer_h-inner_h+strip_h;
            step_h = 0.1;
            for (i = [0:0.1:strip_depth+0.1]){
                translate([0, 0, start_h-step_h + i]){
                    linear_extrude(height = i){
                        offset(r = -i, chamfer = true){
                            projection(){
                                cut_part();
                            }
                        }
                    }
                }
            }
        }
    }
}

// Відображення фінальної моделі
difference(){
    original_part();
union(){
    rounding();
    cut_part();
    //color("black"){translate([0,0,25*2-5]){mirror([0,0,1]){rounding();}}}
}
}

*cut_part();
*rounding();