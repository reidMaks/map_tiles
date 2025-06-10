base_path = "C:/Users/38066/Desktop/base.stl";

base_h = 16;
lid_h = 4;
module lid(){
color("red"){
    translate([0,0, base_h-(lid_h/1.2)]){
    linear_extrude(height = lid_h) {
        offset(r = -3) {
            
            projection(cut = true) {
                import(base_path);
            }
        }
    }
    
    }
}
}
module body(){
color("green", 0.5){
    import(base_path);
    }
}
  

module cut(){
    color("orange"){
        translate([0,0, base_h-lid_h]){
    linear_extrude(height = lid_h) {
        offset(r = -4.1) {
            
            projection(cut = true) {
                import(base_path);
            }
        }
    }
    
    }
        }}
        
module rounding(){
    color("blue"){
        union(){
            start_h = base_h-lid_h-2;
            step_h = 0.1;
            for (i = [0:0.1:3+0.1]){
                translate([0, 0, start_h-step_h + i]){
                    linear_extrude(height = i){
                        offset(r = -i, chamfer = true){
                            projection(){
                                cut();
                            }
                        }
                    }
                }
            }
        }
    }
}
difference(){
    lid();
    body();
    *cut();
    rounding();
    }
    *lid();
 *cut();
 *rounding();