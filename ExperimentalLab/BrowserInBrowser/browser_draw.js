$(document).ready(function () {
    $("#drawing").click(function () {
        drawIframe();
    });

    function drawIframe() {
        $("#target").attr("src", $("#inputUrl").val())
    }

});