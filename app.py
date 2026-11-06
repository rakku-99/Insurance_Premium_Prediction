from flask import Flask, request, render_template
import math
import pandas as pd
import pickle

app = Flask(__name__)

file = open("./gradient_boosting_regressor_model.pkl", 'rb')
model = pickle.load(file)

data = pd.read_csv('./clean_data.csv')
data.head()

@app.route('/')
def index():
    sex = sorted(data['sex'].unique())
    smoker = sorted(data['smoker'].unique())
    region = sorted(data['region'].unique())
    return render_template('index.html', sex= sex, smoker= smoker, region= region)

@app.route('/predict', methods=['POST'])
def predict():
    age_value = request.form.get('age', '').strip()
    try:
        age = int(age_value)
    except ValueError:
        return "Age must be a whole number between 1 and 130.", 400
    if not 1 <= age <= 130:
        return "Age must be between 1 and 130.", 400
    sex = request.form.get('sex')
    weight_value = request.form.get('weight', '').strip()
    height_value = request.form.get('height', '').strip()
    if bool(weight_value) != bool(height_value):
        return "Enter both weight and height to calculate BMI, or leave both blank.", 400
    if weight_value and height_value:
        try:
            weight = float(weight_value)
            height = float(height_value)
        except ValueError:
            return "Weight and height must be valid numbers greater than 0.", 400
        if not math.isfinite(weight) or not math.isfinite(height):
            return "Weight and height must be finite numbers.", 400
        if not 0 < weight <= 300:
            return "Weight must be greater than 0 and no more than 300 kg.", 400
        if not 50 <= height <= 250:
            return "Height must be between 50 and 250 cm.", 400
        bmi = weight / ((height / 100) ** 2)
    else:
        try:
            bmi = float(request.form.get('bmi', '').strip())
        except ValueError:
            return "Enter a valid BMI, or provide both weight and height.", 400
    if not math.isfinite(bmi) or not 0 < bmi <= 53.1:
        if weight_value and height_value:
            return (
                "Calculated BMI must be no more than 53.1. Check the height first; "
                "if it is correct, verify the weight.",
                400,
            )
        return "BMI must be greater than 0 and no more than 53.1.", 400
    children_value = request.form.get('children', '').strip()
    try:
        children = int(children_value) if children_value else 0
    except ValueError:
        return "Number of children must be a whole number between 0 and 10.", 400
    if not 0 <= children <= 10:
        return "Number of children must be between 0 and 10.", 400
    smoker = request.form.get('smoker')
    region = request.form.get('region')

    prediction = model.predict(
        pd.DataFrame([[age, sex, bmi, children, smoker, region]], 
        columns=['age', 'sex', 'bmi', 'children', 'smoker', 'region']))

    return str(prediction[0])           

if __name__=="__main__":
    app.run(debug=True,port=1947)
