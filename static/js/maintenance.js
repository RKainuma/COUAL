'use strict';

$(function(){
    $("#neg-color-plus-btn").on("click", function(){
        let num_of_colors = $(this).attr('data-num');
        let next_num_of_colors = Number(num_of_colors)+1
        $(this).attr('data-num', next_num_of_colors);
        let neg_color_elm = '<p><span>アクセントカラーHSV</span><br><input type ="text" name="neg'+next_num_of_colors+'" required="required"> <br>色の名前<br><input type ="text" name="neg'+next_num_of_colors+'-name" required="required"><br>-------------------------------------</p>'
        $(this).prev().after(neg_color_elm);
        $("#neg-color-minus-btn").show();
    });
});

$(function(){
    $("#neg-color-minus-btn").on("click", function(){
        let num_of_colors = $(this).prev().attr('data-num');
        let next_num_of_colors = Number(num_of_colors)-1
        $(this).prev().attr('data-num', next_num_of_colors);
        $(this).prev().prev().remove();
        if (next_num_of_colors == 1) {
            $(this).hide();
        }
    });
});

$(function(){
    $("#pos-color-plus-btn").on("click", function(){
        let num_of_colors = $(this).attr('data-num');
        let next_num_of_colors = Number(num_of_colors)+1
        $(this).attr('data-num', next_num_of_colors);
        let neg_color_elm = '<p><span>アクセントカラーHSV</span><br><input type ="text" name="pos'+next_num_of_colors+'" required="required"> <br>色の名前<br><input type ="text" name="pos'+next_num_of_colors+'-name" required="required"><br>-------------------------------------</p>'
        $(this).prev().after(neg_color_elm);
        $("#pos-color-minus-btn").show();
    });
});

$(function(){
    $("#pos-color-minus-btn").on("click", function(){
        let num_of_colors = $(this).prev().attr('data-num');
        let next_num_of_colors = Number(num_of_colors)-1
        $(this).prev().attr('data-num', next_num_of_colors);
        $(this).prev().prev().remove();
        if (next_num_of_colors == 1) {
            $(this).hide();
        }
    });
});

