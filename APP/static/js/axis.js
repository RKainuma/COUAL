$(document).ready(function () {
    $(".axis_color").click(function () {
        var selectedColor = $(this).css('backgroundColor');
        $('#axis_color_seleced').css('background-color', selectedColor);
    });

    $("#axis_switch_svg").click(function () {
        $('#xAxis').toggle();
        $('#yAxis').toggle();
    });

    $("#original").mousemove(function (e) {
        axesDrawing(e, $(this));
    });

    $("#analyzed").mousemove(function (e) {
        axesDrawing(e, $(this));
    });

    function axesDrawing(e, ele) {
        var axisColor = $("#axis_color_seleced").css('backgroundColor');
        // X軸の操作
        $('#yAxis').css('background-color', axisColor);
        $('#yAxis').offset({
            left: e.pageX - 1,
            top: ele.offset().top
        });
        $('#yAxis').height(ele.height());

        // Y軸の操作
        $('#xAxis').css('background-color', axisColor);
        $('#xAxis').offset({
            left: ele.offset().left,
            top: e.pageY - 1
        });
        $('#xAxis').width(ele.width());
    }
});