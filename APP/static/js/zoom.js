$(document).ready(function () {
    $(window).resize(function () {
        $("html").height($("#main").height() + $("#original").height());
        $("body").height($("#main").height() + $("#original").height());
        $("#sidebar_div").height($("#main").height() + $("#original").height());
    });
});