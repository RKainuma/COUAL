'use strict';

$(document).ready(function () {
    $("#analyze").click(function () {
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
        var originalContext = originalCanvas.getContext('2d')
        var originalImg = new Image();
        originalImg.src = originalImgSrc;
        originalImg.onload = function () {
            originalContext.drawImage(originalImg, 0, 0, 200, 200);
        }
        var analyzedCanvas = document.getElementById("analyzed")
        var analyzedContext = analyzedCanvas.getContext('2d')
        var analyzedImg = new Image();
        analyzedImg.src = analyzedImgSrc;
        analyzedImg.onload = function () {
            analyzedContext.drawImage(analyzedImg, 0, 0, 200, 200);
        }
    }
});