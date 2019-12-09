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

    $("#BGR2RGB").click(function () {
        kickAxios('/bgrtorgb');
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
            .then(data => drawImage(data.original_img, data.analyzed_img))
            .catch(errorAction)
    }

    function drawImage(originalImgSrc, analyzedImgSrc) {
        var originalImage = document.getElementById("original")
        originalImage.src = "data:image/jpeg;base64," + originalImgSrc;
        var analyzedImage = document.getElementById("analyzed")
        analyzedImage.src = "data:image/jpeg;base64," + analyzedImgSrc;
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