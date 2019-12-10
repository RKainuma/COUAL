$(document).ready(function () {
    $("#original").mousewheel(function (eo, delta, deltaX, deltaY) {
        e.preventDefault();
        var imageWidth = $("#original").width();
        var imageHeight = $("#original").height();

        if (deltaY < 0) {
            $("#original").width(imageWidth + 50);
            $("#original").css('height', imageHeight + (50 * imageHeight / imageWidth));
        } else {
            $("#original").width(imageWidth - 50);
            $("#original").css('height', imageHeight + (-50 * imageHeight / imageWidth));
        }
    });
});