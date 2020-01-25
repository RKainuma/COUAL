from flask import Flask, render_template, request, jsonify

from valid_color_diff import proceed_color_diff

app = Flask(__name__)


@app.route("/")
def index():
    return render_template('index.html')

@app.route("/post", methods=["POST"])
def post():
    baseHex, mainHex, accentHex = request.form["base"], request.form["main"], request.form["accent"]
    baseRGB, mainRGB, accentRGB  = hex_to_rgb(baseHex), hex_to_rgb(mainHex), hex_to_rgb(accentHex)

    print("Base: {} // Main: {} // Accent: {}".format(baseHex, mainHex, accentHex))
    print("Base: {} // Main: {} // Accent: {}".format(baseRGB, mainRGB, accentRGB))

    base_and_main = proceed_color_diff(baseRGB, mainRGB)
    base__and_accent = proceed_color_diff(baseRGB, accentRGB)
    main_and_accent = proceed_color_diff(mainRGB, accentRGB)

    base_accent_result = {'common_diff': base__and_accent[1], 'protan_diff': base__and_accent[2], 'dutan_diff': base__and_accent[3]}
    base_main_result = {'common_diff': base_and_main[1], 'protan_diff': base_and_main[2], 'dutan_diff': base_and_main[3]}
    main_accent_result = {'common_diff': main_and_accent[1], 'protan_diff': main_and_accent[2], 'dutan_diff': main_and_accent[3]}

    return jsonify({'base_main': base_main_result, 'base_accent': base_accent_result, 'main_accent': main_accent_result})


def hex_to_rgb(val):
    val = val.lstrip('#')
    lv = len(val)

    return tuple(int(val[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
