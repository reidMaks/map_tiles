

// [Number] Висота екструдування
origin_height = 40;
hight_above_lid = 2*0.4;
hight_below_lid = 2;

// [Vector] Фактор масштабування
scale_factor = [0.4, 0.4, 1]; 


// [String] Шлях до STL файлу
path_to_stl = "C:/Users/38066/Desktop/map_tiles/stl/sums'ka.stl"; 

module proj_offset(_offset){
    
    offset(r=_offset, chamfer = true){
    projection(cut = true) {
                import(path_to_stl);
     }
}
    
}
module lid_top(){
translate([0,0, origin_height]){
    linear_extrude(height = hight_above_lid) {
        proj_offset(-5);
    }
}}



module lid_botom(){
color("violet"){ 
    translate([0,0, origin_height - hight_below_lid]){
linear_extrude(height = hight_below_lid) {    

    difference(){
    proj_offset(-10.3);
    proj_offset(-12.6);
        
    }

            
}}}}


module original_part(){
color("green"){
import(path_to_stl);
}
}

scale(scale_factor){
union(){
lid_top();
lid_botom();
}
}