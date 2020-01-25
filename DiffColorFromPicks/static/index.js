'use strict'
$(document).ready(function() {
    $('#calc-diff').on('click', function (event) {
        $.ajax({
            data: { base: $('#base').val(), main: $('#main').val(), accent: $('#accent').val() },
            type: 'POST',
            url: '/post'
        })
        .done(function (data) {
            show_diff_result(data.base_main, data.base_accent, data.main_accent)
        });
        event.preventDefault();
    });
    function show_diff_result (base_main, base_accent, main_accent) {
        $('#bm-c-jis').text(gen_result_msg(base_main.common_diff.JIS.label));
        $('#bm-c-score').text(base_main.common_diff.result);
        $('#bm-d-jis').text(gen_result_msg(base_main.dutan_diff.JIS.label));
        $('#bm-d-score').text(base_main.dutan_diff.result);
        $('#bm-p-jis').text(gen_result_msg(base_main.protan_diff.JIS.label));
        $('#bm-p-score').text(base_main.protan_diff.result);

        $('#ba-c-jis').text(gen_result_msg(base_accent.common_diff.JIS.label));
        $('#ba-c-score').text(base_accent.common_diff.result);
        $('#ba-d-jis').text(gen_result_msg(base_accent.dutan_diff.JIS.label));
        $('#ba-d-score').text(base_accent.dutan_diff.result);
        $('#ba-p-jis').text(gen_result_msg(base_accent.protan_diff.JIS.label));
        $('#ba-p-score').text(base_accent.protan_diff.result);

        $('#ma-c-jis').text(gen_result_msg(main_accent.common_diff.JIS.label));
        $('#ma-c-score').text(main_accent.common_diff.result);
        $('#ma-d-jis').text(gen_result_msg(main_accent.dutan_diff.JIS.label));
        $('#ma-d-score').text(main_accent.dutan_diff.result);
        $('#ma-p-jis').text(gen_result_msg(main_accent.protan_diff.JIS.label));
        $('#ma-p-score').text(main_accent.protan_diff.result);
    }

    function gen_result_msg(label) {
        if (label == "FINE") {
            var msg = '別の色'
        } else if (label == 'D') {
            var msg = 'D級許容色差'
        } else if (label == 'C') {
            var msg = 'C級許容色差'
        } else if (label == 'B') {
            var msg = 'B級許容色差'
        } else if (label == 'A') {
            var msg = 'A級許容色差'
        } else if (label == 'AA') {
            var msg = 'AA級許容色差'
        } else if (label == 'AAA') {
            var msg = 'AAA級許容色差'
        } else if (label == 'LIMIT') {
            var msg = '識別限界'
        } else if (label == 'UNEVALUABLE') {
            var msg = '"評価不能領域"'
        } else {
            var msg = 'メッセージハンドルできてない'
        }
        return msg
    }
});

$(function(){
    $("input[type=color]").on('change', function () {
        let colorObj = convert_color_object($(this).val());
        let target_p = $(this).attr('name');
        append_rgb_msg(colorObj, target_p)
    });

    function convert_color_object (hex) {
        let colorObj = new RGBColor(hex);
        return colorObj;
    };

    function append_rgb_msg(colorObj, target_p) {
        $('#' + target_p + '_rgb').text(colorObj.toRGB());
    };
});
