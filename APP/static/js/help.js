$(document).ready(function () {
    $("#help_color_vision").click(function () {
        displayHelp(helpColorVision);
    });

    $("#help_gray_scale").click(function () {
        displayHelp(helpGrayScale);
    });

    $("#help_binarization").click(function () {
        displayHelp(helpBinarization);
    });

    $("#help_edge_detection").click(function () {
        displayHelp(helpEdgeDetection);
    });

    $("#help_bgr_rgb").click(function () {
        displayHelp(helpBgrRgb);
    });

    $("#help_singularity").click(function () {
        displayHelp(helpSingularity);
    });

    $("#help_hide").click(function () {
        $('#help_area').hide();
    });

    function displayHelp(message) {
        $('#help_message').text(message);
        $('#help_area').show();
    }

    var helpColorVision = "色覚判断の説明";
    var helpGrayScale = "コンピュータ上及び写真での色の表現方法の一種。デジタル画像の中でも、ピクセルの標本値に光度以外の情報が含まれていない画像のこと。グレースケールでは、二値画像と異なり、画像を光が最も強い白から最も弱い黒まで間の灰色の明暗も含めて表現する";
    var helpBinarization = "二値画像（にちがぞう）またはバイナリイメージ（英語: binary image）とは、各ピクセルの取り得る値が2種類のみのデジタル画像。一般的に、 二値画像に使用される2つの色は白と黒であるが、 これら以外の任意の色の組み合わせも使用することができる。 画像内のオブジェクトに使用される色は前景色(foreground color) であり、 残りの画像は背景色(background color) 。 文書スキャニングの分野では、 バイトーナル(bi-tonal) と呼ばれる。二値画像は、 各ピクセルが単一のビット、 すなわち0または1として記録される。 二値画像のことを「 白黒」(black-and-white) や「 モノクローム」(monochrome) などと呼ぶこともあるが、 これらの名称は、 各ピクセルについて単一の周波数の光のみをサンプリングした画像（ グレースケールなど） についても用いられる。 Photoshopでは、 バイナリイメージはビットマップモードのイメージと同じ意味。";
    var helpEdgeDetection = "エッジ検出（エッジけんしゅつ、英: edge detection）は、画像処理やコンピュータビジョンの用語で、特徴検出 (feature detection) や特徴抽出 (feature extraction) の一種であり、デジタル画像の画像の明るさが鋭敏に、より形式的に言えば不連続に変化している箇所を特定するアルゴリズムを指す。";
    var helpBgrRgb = "BGR to RGB の説明";
    var helpSingularity = "特異点抽出の説明";
})