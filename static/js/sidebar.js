$(document).ready(function () {
    $("#histogram").click(function () {
        kickAxios('/histogram', document.getElementById("fileInput").files[0]);
    });

    function kickAxios(method, image) {
        if (fileInput.files.length <= 0) {
            alert("画像を選択してください。");
            return;
        }
        if ((fileInput.value.toUpperCase().indexOf('PNG') == -1) && (fileInput.value.toUpperCase().indexOf('JPG') == -1)) {
            alert('添付ファイルの形式（拡張子）が違います。');
            return;
        }
        var params = new FormData();
        var instance = axios.create({
            'responseType': 'json',
            'headers': {
                'Content-Type': 'application/json'
            }
        });
        params.append('img_file', image)

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
        analyzeImage(instance, params)
            .catch(errorAction)
    }
});