# app.py
import json
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

def percentile2z(percentile):
    return norm.ppf(percentile / 100)
    # reverse z2percentile
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
    print(L,M,S, z)
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

@app.route("/predictHeightForPercentile", methods=["POST"])
def predict_height_for_percentile():
    prediction_ages = [0] + [i + 0.5 for i in range(0, 240)] + [240]
    percentiles= [5,10,25,50,75,90,95]
    # convert percentile to zindex
    zindex = []
    for percentile in percentiles:
        zindex.append(percentile2z(percentile))
    
    # get height for each zindex
    heights = {}
    for z in zindex:
        heights[round(z2percentile(z))] = {}

        heights[round(z2percentile(z))]["male"] = {}
        heights[round(z2percentile(z))]["female"] = {}
        for age in prediction_ages:
            heights[round(z2percentile(z))]["male"][age] = {}
            if age < 36:
                maleHeight = get_weight_nonzero(age, z, 1, heightdf)
                femaleHeight = get_weight_nonzero(age, z, 2, heightdf)
                heights[round(z2percentile(z))]["male"][age] = round(maleHeight, 2)
                heights[round(z2percentile(z))]["female"][age] = round(femaleHeight, 2)
            else:
                maleHeight = get_weight_nonzero(age, z, 1, heightabovedf)
                femaleHeight = get_weight_nonzero(age, z, 2, heightabovedf)
                heights[round(z2percentile(z))]["male"][age] = round(maleHeight, 2)
                heights[round(z2percentile(z))]["female"][age] = round(femaleHeight, 2)
    # save to json file named heightData.json
    with open('heightData.json', 'w') as fp:
        json.dump(heights, fp)
    return jsonify(heights)

@app.route("/getHeightPercentile", methods=["GET"])
def get_height_percentile():
    with open('heightData.json') as json_file:
        data = json.load(json_file)
        return jsonify(data)

@app.route("/predictWeightForPercentile", methods=["POST"])
def predict_weight_for_percentile():
    prediction_ages = [0] + [i + 0.5 for i in range(0, 240)] + [240]
    percentiles= [5,10,25,50,75,90,95]
    # convert percentile to zindex
    zindex = []
    for percentile in percentiles:
        zindex.append(percentile2z(percentile))
    
    # get weight for each zindex
    weights = {}
    for z in zindex:
        weights[round(z2percentile(z))] = {}

        weights[round(z2percentile(z))]["male"] = {}
        weights[round(z2percentile(z))]["female"] = {}
        for age in prediction_ages:
            weights[round(z2percentile(z))]["male"][age] = {}
            if age < 36:
                maleWeight = get_weight_nonzero(age, z, 1, weightdf)
                femaleWeight = get_weight_nonzero(age, z, 2, weightdf)
                weights[round(z2percentile(z))]["male"][age] = round(maleWeight, 2)
                weights[round(z2percentile(z))]["female"][age] = round(femaleWeight, 2)
            else:
                maleWeight = get_weight_nonzero(age, z, 1, weightabovedf)
                femaleWeight = get_weight_nonzero(age, z, 2, weightabovedf)
                weights[round(z2percentile(z))]["male"][age] = round(maleWeight, 2)
                weights[round(z2percentile(z))]["female"][age] = round(femaleWeight, 2)
    # save to json file named weightData.json
    with open('weightData.json', 'w') as fp:
        json.dump(weights, fp)
    return jsonify(weights)

@app.route("/getWeightPercentile", methods=["GET"])
def get_weight_percentile():
    with open('weightData.json') as json_file:
        data = json.load(json_file)
        return jsonify(data)

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
    app.run(threaded=True, debug=True)
