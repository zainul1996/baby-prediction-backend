# baby-prediction-backend

Flask backend that contains the following API end points:<br />

- [x] Predict Weight of a Baby<br />

```
POST /predictWeight
```

Sample Request:

```JSON
{
    "current_age": 0,
    "current_weight":4.2,
    "sex":"male"
}
```

Sample Response:

```JSON
{
    "percentile": 90.99,
    "predicted_weight": {
        "0": 4.2,
        "0.5": 4.75,
        "1.5": 5.77,
        "2.5": 6.68,
        "3.5": 7.51,
        "4.5": 8.26,
        "5.5": 8.93,
        "6.5": 9.54,
        "7.5": 10.09,
        "8.5": 10.59,
        "9.5": 11.03,
        "10.5": 11.44,
        "11.5": 11.81,
        "12.5": 12.15,
        "13.5": 12.45,
        "14.5": 12.74,
        "15.5": 13.0,
        "16.5": 13.24,
        "17.5": 13.46,
        "18.5": 13.67,
        "19.5": 13.87,
        "20.5": 14.06,
        "21.5": 14.24,
        "22.5": 14.42,
        "23.5": 14.59,
        "24.5": 14.76,
        "25.5": 14.93,
        "26.5": 15.1,
        "27.5": 15.26,
        "28.5": 15.43,
        "29.5": 15.6,
        "30.5": 15.77,
        "31.5": 15.95,
        "32.5": 16.12,
        "33.5": 16.3,
        "34.5": 16.48,
        "35.5": 16.67,
        "36": 16.76
    }
}
```

- [x] Predict Height of a Baby<br />

```
POST /predictHeight
```

Sample Request:

```JSON
{
    "current_age": 0,
    "current_height":50,
    "sex":"male"
}
```

Sample Response:

```JSON
{
    "percentile": 50.17,
    "predicted_height": {
        "0": 50.0,
        "0.5": 52.71,
        "1.5": 56.64,
        "2.5": 59.62,
        "3.5": 62.09,
        "4.5": 64.23,
        "5.5": 66.14,
        "6.5": 67.87,
        "7.5": 69.47,
        "8.5": 70.96,
        "9.5": 72.36,
        "10.5": 73.68,
        "11.5": 74.93,
        "12.5": 76.13,
        "13.5": 77.28,
        "14.5": 78.38,
        "15.5": 79.44,
        "16.5": 80.47,
        "17.5": 81.46,
        "18.5": 82.42,
        "19.5": 83.35,
        "20.5": 84.26,
        "21.5": 85.15,
        "22.5": 86.01,
        "23.5": 86.85,
        "24.5": 87.68,
        "25.5": 88.47,
        "26.5": 89.24,
        "27.5": 89.99,
        "28.5": 90.73,
        "29.5": 91.44,
        "30.5": 92.15,
        "31.5": 92.84,
        "32.5": 93.51,
        "33.5": 94.17,
        "34.5": 94.82,
        "35.5": 95.46
    }
}
```

- [x] Calculates BMI of a baby<br />

```
POST /calculateBMI
```

Sample Request:

```JSON
{
    "current_weight":4.2,
    "current_height":50
}
```

Sample Response:

```JSON
{
    "bmi": 16.8
}
```

## Setup

1. Clone Repository

```bash
git clone https://github.com/zainul1996/baby-prediction-backend.git
```

2. cd into project and install dependancies

```bash
cd baby-prediction-backend && pip install -r requirements.txt
```

3. Run Server

```bash
python app.py
```
