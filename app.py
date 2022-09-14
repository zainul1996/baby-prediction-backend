# app.py
from flask import Flask, request, jsonify, render_template
import math
import pandas as pd
from scipy.stats import norm


app = Flask(__name__)
pd.set_option("display.precision", 12)
weightdf = pd.read_csv("wtageinf.csv", parse_dates=False)


def get_LMS(age, sex):
    age = age + 0.5
    tempdf = weightdf[(weightdf["Agemos"] == age) & (weightdf["Sex"] == sex)]
    return tempdf[["L", "M", "S"]]


def z2percentile(z):
    return norm.cdf(z) * 100


def get_percentile(age, weight, sex):
    lmsdf = get_LMS(age, sex)
    # Z = ln(X/M)/S
    return math.log(weight / lmsdf["M"]) / lmsdf["S"]


def get_weight(age, z, sex):
    lmsdf = get_LMS(age, sex)
    return lmsdf["M"] * math.exp(lmsdf["S"] * z)


@app.route("/predictWeight", methods=["POST"])
def predict_weight():
    data = request.get_json()
    current_age = data["current_age"]
    print("current_age:", current_age)
    weight = data["current_weight"]
    print("current_weight:", weight)
    sex = data["sex"]
    print("sex:", sex)
    prediction_age = data["prediction_age"]
    print("prediction_age:", prediction_age)

    if sex == "male":
        sex = 1
    elif sex == "female":
        sex = 2
    else:
        return jsonify({"ERROR": "incorrect sex provided"})

    print("sex:", sex)

    zindex = get_percentile(current_age, weight, sex)
    print("z:", zindex.values[0])
    percentile = z2percentile(zindex.values[0])
    print("percentile:", percentile)
    predicted_weight = get_weight(prediction_age, zindex.values[0], sex)
    print("weight:", predicted_weight.values[0])

    return jsonify(
        {
            "predicted_weight": round(predicted_weight.values[0], 2),
            "percentile": round(percentile, 2),
        }
    )


# A welcome message to test our server
@app.route("/")
def index():
    return "<h1>Welcome to our server !!</h1>"


if __name__ == "__main__":
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5000, debug=True)
