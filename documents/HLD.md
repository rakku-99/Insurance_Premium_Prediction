# High-Level Design (HLD)

**Project:** Insurance Premium Prediction App  
**Prepared by:** Rakesh Ranjan  
**Document scope:** Current packaged Flask application

## 1. Purpose

The application collects a user's demographic and health-related inputs and returns a predicted insurance premium from a pre-trained Gradient Boosting regression model. The output is an estimate produced by the model, not an insurance quote.

## 2. Scope and actors

- **User:** Opens the web form, enters required details, optionally supplies height and weight to calculate BMI, and requests a prediction.
- **Flask application:** Renders dropdowns and the input form, validates submissions, derives BMI when requested, invokes the model, and returns a result or input error.
- **Model and data files:** A serialized scikit-learn pipeline/model provides predictions. `clean_data.csv` supplies the selectable category values.

Training, model selection, account management, payment, policy issuance, and a production hosting platform are outside the current app runtime.

## 3. Context and component view

```text
+-------------------+
| User's browser    |
| HTML form + JS    |
+---------+---------+
          | GET /
          | POST /predict (form fields)
          v
+---------+---------+      +--------------------+
| Flask application |----->| clean_data.csv     |
| routes + checks   |      | dropdown choices   |
+---------+---------+      +--------------------+
          |
          | validated feature row
          v
+---------+---------+
| Pre-trained       |
| sklearn model     |
+---------+---------+
          |
          | predicted premium
          v
   Browser displays result
```

## 4. Main request flows

### Form rendering

1. Browser requests `GET /`.
2. Flask loads unique `sex`, `smoker`, and `region` values from `clean_data.csv`.
3. Flask renders `templates/index.html` with those option lists.
4. Browser displays the form and JavaScript BMI helper.

### Prediction

1. Browser validates HTML constraints and its custom weight/height pairing checks.
2. JavaScript posts form data to `POST /predict`.
3. Flask performs authoritative server-side parsing and validation.
4. If weight and height are both present, Flask calculates BMI; otherwise it parses the manually entered BMI.
5. Flask builds a one-row pandas DataFrame in the model's expected feature order and calls `model.predict`.
6. Flask returns the prediction as response text. The browser displays it. Invalid input returns an explanatory message with HTTP 400.

## 5. Runtime components and dependencies

- Python and Flask provide the web server and routing.
- pandas constructs the model input DataFrame and reads category values from CSV.
- scikit-learn loads and runs the serialized model.
- HTML, CSS, and JavaScript implement the browser interface and BMI helper.
- `gradient_boosting_regressor_model.pkl` and `clean_data.csv` must be available relative to the app's working directory.
- The pickle was recorded with scikit-learn 1.2.0; use that version when loading it.

## 6. Input rules and model-range considerations

- Age: whole number from 1 to 130.
- Weight: optional; if supplied, finite, greater than 0, and no more than 300 kg.
- Height: optional; if supplied, finite and between 50 and 250 cm. The 50 cm minimum is an application input floor, not a medical standard.
- Weight and height must either both be supplied or both be blank.
- BMI: finite, greater than 0, and no more than 53.1.
- Children: blank defaults to 0; otherwise a whole number from 0 to 10.
- Sex, smoker status, and region are supplied from the values in `clean_data.csv`.

The cleaned data inspected for this package spans ages 18–64, BMI 16.0–53.1, and children 0–5. The accepted age and children limits are broader than the observed training data, so predictions for ages or child counts beyond those observed ranges may be extrapolations. The BMI maximum matches the observed dataset maximum. Weight and height limits are broad sanity limits; calculated BMI must still satisfy the BMI validation.

## 7. Operational and security notes

- The packaged `app.py` starts Flask on port 1947 with debug mode enabled for local development. Debug mode must be disabled and a production WSGI server used before public deployment.
- Only load the pickle model file distributed with or otherwise trusted by the application; pickle loading can execute code.
- The current app has no authentication, persistence, or request throttling.
- The browser provides convenience checks, but the server is the authoritative validation boundary.

## 8. Key files

| File | Responsibility |
|---|---|
| `app.py` | Flask routes, input validation, BMI calculation, model invocation |
| `templates/index.html` | Form markup, client-side BMI calculation, AJAX submission |
| `static/css/style.css` | Page styling |
| `clean_data.csv` | Dropdown option source |
| `gradient_boosting_regressor_model.pkl` | Trained prediction model |
| `requirements.txt` | App-specific Python dependency pins |
