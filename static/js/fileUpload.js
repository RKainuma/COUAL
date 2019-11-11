'use strict';

$(document).ready(function () {
    $("#analyze").click(function () {
        if (fileInput.files.length <= 0) {
            alert("画像を選択してください。");
            return;
        }
        console.log(fileInput.value.toUpperCase().indexOf('PNG'));
        console.log(fileInput.value.toUpperCase().indexOf('JPG'));
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
                    .post('/send', params)
                    .then(response => resolve(response.data))
                    .catch(error => reject(error.response.status))
            });
        }
        analyzeImage(instance, params)
            .then(data => drawCanvas(data.original_img, data.analyzed_img))
            .catch(statusCode => console.error("サーバーとの通信に失敗しました。:", statusCode))
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

    function drawCanvas(originalImgSrc, analyzedImgSrc) {
        var originalCanvas = document.getElementById("original")
        //var originalContext = originalCanvas.getContext('2d')
        //var originalImg = new Image();
        originalCanvas.src = "data:image/jpeg;base64," + originalImgSrc;
        // originalImg.onload = function () {
        //     var w = $("#original").width() * 40 / 100;
        //     var h = $("#original").height() * 40 / 100;
        //     console.log(w);
        //     console.log(h);
        //     originalCanvas.drawImage(originalImg, 0, 0, w, h);
        // }
        var analyzedCanvas = document.getElementById("analyzed")
        // var analyzedContext = analyzedCanvas.getContext('2d')
        // var analyzedImg = new Image();
        analyzedCanvas.src = "data:image/jpeg;base64," + analyzedImgSrc;
        // analyzedImg.onload = function () {
        //     var w = $("#analyzed").width() * 35 / 100;
        //     var h = $("#analyzed").height() * 35 / 100;
        //     analyzedContext.drawImage(analyzedImg, 0, 0, w, h);
        // }
    }
});