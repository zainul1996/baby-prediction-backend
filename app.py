# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import os
import pandas as pd
from scipy.stats import norm


app = Flask(__name__)
CORS(app)
pd.set_option("display.precision", 12)
weightdf = pd.read_csv("wtageinf.csv", parse_dates=False)
weightabovedf = pd.read_csv('wtage.csv', parse_dates=False)
heightdf = pd.read_csv("lenageinf.csv", parse_dates=False)
heightabovedf = pd.read_csv('statage.csv', parse_dates=False)


def get_LMS(age, sex, df):
    tempdf = df[(df["Agemos"] == age) & (df["Sex"] == sex)]
    return tempdf[["L", "M", "S"]]


def z2percentile(z):
    return norm.cdf(z) * 100


def get_percentile(age, weight, sex, df):
    lmsdf = get_LMS(age, sex, df)
    percentile = math.log(weight / lmsdf["M"]) / lmsdf["S"]
    return percentile.values[0]


def get_percentile_nonzero(age, weight, sex, df):
    lmsdf = get_LMS(age, sex, df)
    L = lmsdf["L"].values[0]
    M = lmsdf["M"].values[0]
    S = lmsdf["S"].values[0]
    percentile = (((weight / M) ** L) - 1) / (L * S)
    return percentile


def get_weight(age, z, sex, df):
    lmsdf = get_LMS(age, sex, df)
    return lmsdf["M"] * math.exp(lmsdf["S"] * z)


def get_weight_nonzero(age, z, sex, df):
    lmsdf = get_LMS(age, sex, df)
    L = lmsdf["L"].values[0]
    M = lmsdf["M"].values[0]
    S = lmsdf["S"].values[0]
    return M * ((L * S * z) + 1) ** (1 / L)

@app.route("/visitorCount", methods=["POST"])
def visitorCount():
    if os.path.exists("count.csv"):
        countdf = pd.read_csv("count.csv")
        count = countdf["count"].values[0]
        count += 1
        countdf["count"] = count
        countdf.to_csv("count.csv", index=False)
    else:
        countdf = pd.DataFrame({"count": [1]})
        countdf.to_csv("count.csv", index=False)
    return jsonify({"count": count})


@app.route("/predictWeight", methods=["POST"])
def predict_weight():
    data = request.get_json()
    current_age = data["current_age"]
    weight = data["current_weight"]
    sex = data["sex"]
    prediction_ages = [0] + [i + 0.5 for i in range(0, 36)] + [36]

    if current_age not in prediction_ages:
        return jsonify({"ERROR": "current_age must be in {}".format(prediction_ages)})

    if sex == "male":
        sex = 1
    elif sex == "female":
        sex = 2
    else:
        return jsonify({"ERROR": "incorrect sex provided"})

    zindex = get_percentile_nonzero(current_age, weight, sex, weightdf)
    percentile = z2percentile(zindex)

    prediction_weights = {}
    for age in prediction_ages:
        prediction_weight = get_weight_nonzero(age, zindex, sex, weightdf)
        prediction_weights[age] = round(prediction_weight, 2)

    return jsonify(
        {
            "predicted_weight": prediction_weights,
            "percentile": round(percentile, 2),
        }
    )

@app.route("/predictWeightAll", methods=["POST"])
def predict_weight_abv():
    data = request.get_json()
    current_age = data["current_age"]
    weight = data["current_weight"]
    sex = data["sex"]

    prediction_ages = [0] + [i + 0.5 for i in range(0, 240)] + [240]
    prediction_ages_before = []
    prediction_ages_after = []

    # find index of current age in prediction_ages
    prediction_ages_index = prediction_ages.index(current_age)
    # if there 12 values before it get the 12 values before it
    if prediction_ages_index >= 12:
        prediction_ages_before = prediction_ages[prediction_ages_index - 12:prediction_ages_index]
    # else get all the values before it
    else:
        prediction_ages_before = prediction_ages[:prediction_ages_index + 1]
    
    # if there are 12 values after it get the 12 values after it
    if prediction_ages_index <= len(prediction_ages) - 13:
        prediction_ages_after = prediction_ages[prediction_ages_index+1:prediction_ages_index + 13]
    # else get all the values after it
    else:
        prediction_ages_after = prediction_ages[prediction_ages_index:]

    # join the two lists
    prediction_ages_final = prediction_ages_before + [current_age] + prediction_ages_after

    if current_age not in prediction_ages_final:
        return jsonify({"ERROR": "current_age must be in {}".format(prediction_ages_final)})
    
    if sex == "male":
        sex = 1
    elif sex == "female":
        sex = 2
    else:
        return jsonify({"ERROR": "incorrect sex provided"})
    zindex = 0
    if current_age < 36:
        zindex = get_percentile_nonzero(current_age, weight, sex, weightdf)
    else:
        zindex = get_percentile_nonzero(current_age, weight, sex, weightabovedf)
    percentile = z2percentile(zindex)

    prediction_weights = {}
    for age in prediction_ages_final:
        if age < 36:
            prediction_weight = get_weight_nonzero(age, zindex, sex, weightdf)
        else:
            prediction_weight = get_weight_nonzero(age, zindex, sex, weightabovedf)
        prediction_weights[age] = round(prediction_weight, 2)

    print(prediction_weights)
    return jsonify(
        {
            "predicted_weight": prediction_weights,
            "percentile": round(percentile, 2),
        }
    )

@app.route("/predictHeightAll", methods=["POST"])
def predict_height_all():
    data = request.get_json()
    current_age = data["current_age"]
    height = data["current_height"]
    sex = data["sex"]
    
    prediction_ages = [0] + [i + 0.5 for i in range(0, 240)] + [240]
    prediction_ages_before = []
    prediction_ages_after = []

    # find index of current age in prediction_ages
    prediction_ages_index = prediction_ages.index(current_age)
    # if there 12 values before it get the 12 values before it
    if prediction_ages_index >= 12:
        prediction_ages_before = prediction_ages[prediction_ages_index - 12:prediction_ages_index]
    # else get all the values before it
    else:
        prediction_ages_before = prediction_ages[:prediction_ages_index + 1]
    
    # if there are 12 values after it get the 12 values after it
    if prediction_ages_index <= len(prediction_ages) - 13:
        prediction_ages_after = prediction_ages[prediction_ages_index+1:prediction_ages_index + 13]
    # else get all the values after it
    else:
        prediction_ages_after = prediction_ages[prediction_ages_index:]

    # join the two lists
    prediction_ages_final = prediction_ages_before + [current_age] + prediction_ages_after

    if current_age not in prediction_ages_final:
        return jsonify({"ERROR": "current_age must be in {}".format(prediction_ages_final)})
    
    if sex == "male":
        sex = 1
    elif sex == "female":
        sex = 2
    else:
        return jsonify({"ERROR": "incorrect sex provided"})

    zindex = 0
    if current_age < 36:
        zindex = get_percentile_nonzero(current_age, height, sex, heightdf)
    else:
        zindex = get_percentile_nonzero(current_age, height, sex, heightabovedf)
    percentile = z2percentile(zindex)

    prediction_heights = {}
    for age in prediction_ages_final:
        if age < 36:
            prediction_height = get_weight_nonzero(age, zindex, sex, heightdf)
        else:
            prediction_height = get_weight_nonzero(age, zindex, sex, heightabovedf)
        prediction_heights[age] = round(prediction_height, 2)
        
    return jsonify(
        {
            "predicted_height": prediction_heights,
            "percentile": round(percentile, 2),
        }
    )

@app.route("/predictHeight", methods=["POST"])
def predict_height():
    data = request.get_json()
    current_age = data["current_age"]
    height = data["current_height"]
    sex = data["sex"]
    prediction_ages = [0] + [i + 0.5 for i in range(0, 36)]

    if current_age not in prediction_ages:
        return jsonify({"ERROR": "current_age must be in {}".format(prediction_ages)})

    if sex == "male":
        sex = 1
    elif sex == "female":
        sex = 2
    else:
        return jsonify({"ERROR": "incorrect sex provided"})

    zindex = get_percentile_nonzero(current_age, height, sex, heightdf)
    percentile = z2percentile(zindex)

    prediction_heights = {}
    for age in prediction_ages:
        prediction_height = get_weight_nonzero(age, zindex, sex, heightdf)
        prediction_heights[age] = round(prediction_height, 2)

    return jsonify(
        {
            "predicted_height": prediction_heights,
            "percentile": round(percentile, 2),
        }
    )


@app.route("/calculateBMI", methods=["POST"])
def calculate_bmi():
    data = request.get_json()
    weight = data["current_weight"]
    height = data["current_height"]
    bmi = weight / (height / 100) ** 2
    return jsonify({"bmi": round(bmi, 2)})


# A welcome message to test our server
@app.route("/")
def index():
    return "<h1>Welcome to our server !!</h1>"


if __name__ == "__main__":
    # Threaded option to enable multiple instances for multiple user access support
    app.run(threaded=True, port=5001, debug=True)
