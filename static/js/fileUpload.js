'use strict';

$(document).ready(function () {
    $("#analyze").click(function () {
        kickAxios('/send');
    });

    $("#gray").click(function () {
        kickAxios('/grayout');
    });

    $("#binarization").click(function () {
        kickAxios('/binarization');
    });

    $("#canny").click(function () {
        kickAxios('/canny');
    });

    function kickAxios(method) {
        if (fileInput.files.length <= 0) {
            alert("画像を選択してください。");
            return;
        }
        if ((fileInput.value.toUpperCase().indexOf('PNG') == -1) && (fileInput.value.toUpperCase().indexOf('JPG') == -1)) {
            alert('添付ファイルの形式（拡張子）が違います。');
            return;
        }
        var params = new FormData();
        var file = document.getElementById("fileInput").files[0]
        var instance = axios.create({
            'responseType': 'json',
            'headers': {
                'Content-Type': 'application/json'
            }
        });
        params.append('img_file', file)

        var analyzeImage = function (instance, params) {
            return new Promise(function (resolve, reject) {
                instance
                    .post(method, params)
                    .then(response => resolve(response.data))
                    .catch(error => reject(error.response.status))
            });
        }
        var errorAction = function () {
            statusCode => console.error("サーバーとの通信に失敗しました。")
            removeLoading()
        }
        dispLoading();
        analyzeImage(instance, params)
            .then(data => drawCanvas(data.original_img, data.analyzed_img))
            .catch(errorAction)
    }

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

    function drawCanvas(originalImgSrc, analyzedImgSrc) {
        var originalCanvas = document.getElementById("original")
        originalCanvas.src = "data:image/jpeg;base64," + originalImgSrc;
        var analyzedCanvas = document.getElementById("analyzed")
        analyzedCanvas.src = "data:image/jpeg;base64," + analyzedImgSrc;
        removeLoading()
    }

    function dispLoading(msg) {
        if ($("#loading").length == 0) {
            $("body").append("<div id='loading'><div class='loadingMsg'></div></div>");
        }
    }

    function removeLoading() {
        $("#loading").remove();
    }
});