'use strict';

$(document).ready(function () {
    $("#analyze").click(function () {
        // ajaxかなんかでpython関数呼ぶ
    });
    var fileArea = document.getElementById('drag-drop-area');
    var fileInput = document.getElementById('fileInput');


    fileArea.addEventListener('dragover', function (evt) {
        evt.preventDefault();
        fileArea.classList.add('dragover');
    });

    fileArea.addEventListener('dragleave', function (evt) {
        evt.preventDefault();
        fileArea.classList.remove('dragover');
    });
    fileArea.addEventListener('drop', function (evt) {
        evt.preventDefault();
        fileArea.classList.remove('dragenter');
        var files = evt.dataTransfer.files;
        fileInput.files = files;
    });
    var ebcp = new EightBitColorPicker({
        el: 'target'
    })

    var el = document.getElementById('target')
    var ebcp = new EightBitColorPicker({
        el: el
    })
});