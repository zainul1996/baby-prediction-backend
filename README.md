# baby-prediction-backend
Flask backend that contains the following API end points:<br />
- [x] Predict Weight of a Baby<br />
```
POST /predictWeight
```
Sample Request:
```JSON
{
    "current_age": 9,
    "current_weight": 9.7,
    "sex": "male",
    "prediction_age": 9
}
```

Sample Response:
```JSON
{
    "percentile": 58.23,
    "predicted_weight": 9.7
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
