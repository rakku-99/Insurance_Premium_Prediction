# Low-Level Design (LLD)

**Project:** Insurance Premium Prediction App  
**Prepared by:** Rakesh Ranjan  
**Implementation source:** `app.py` and `templates/index.html`

## 1. Flask application

### Initialization

At import time, `app.py`:

1. Creates a Flask application.
2. Loads `gradient_boosting_regressor_model.pkl` using `pickle.load`.
3. Reads `clean_data.csv` into a pandas DataFrame.

These resources are loaded once for the process and reused by requests. The app expects the working directory to contain these files.

### `GET /`

The index route:

1. Reads unique values from the `sex`, `smoker`, and `region` columns of the loaded CSV.
2. Sorts each list.
3. Renders `templates/index.html` with those lists.

The template loops over the lists to produce the corresponding select options.

### `POST /predict`

The endpoint accepts form-encoded fields and validates them in this order:

1. **Age:** Trim text, parse as integer, require 1–130.
2. **Weight and height pairing:** Trim both fields. If only one is present, return HTTP 400.
3. **Weight/height path:** If both are present, parse as floats; reject non-finite numbers, weight outside `(0, 300]` kg, or height outside `[50, 250]` cm. The 50 cm minimum is an application input floor, not a medical standard. Calculate:

   `bmi = weight / ((height / 100) ** 2)`

4. **Manual BMI path:** If both weight and height are blank, parse the `bmi` field as a float.
5. **BMI:** Reject non-finite values and values outside `(0, 53.1]`.
6. **Children:** Trim the field; blank becomes `0`, otherwise parse as an integer and require 0–10.
7. **Categorical values:** Read `sex`, `smoker`, and `region` from the form.
8. **Prediction:** Construct a one-row pandas DataFrame with columns in this order:

   `age`, `sex`, `bmi`, `children`, `smoker`, `region`

   Pass it to `model.predict` and return the first predicted value as text.

Input validation errors return a human-readable response and status 400. Model or file-loading errors are not converted into validation responses.

When BMI calculated from a supplied weight/height pair exceeds 53.1, the response asks the user to check height first and verify weight if the height is correct. A manually entered BMI over the limit instead receives a BMI-specific error.

## 2. Browser behavior

The form uses HTML number constraints for numeric fields and `required` for required fields. The weight and height fields are optional but must be entered as a pair.

JavaScript listens for `input` events on weight and height:

- If one is supplied without the other, it marks the missing input invalid and displays a pairing message.
- If both are supplied, it checks the configured bounds, calculates BMI, rounds the displayed BMI to one decimal place, and sets the BMI field.
- If the calculated BMI exceeds 53.1, it marks height invalid and asks the user to check height first, then verify weight if height is correct.
- If both are blank, the visitor may enter BMI directly.

On form submission, JavaScript prevents page navigation, posts `FormData` to `/predict`, and displays either the returned premium or the error message. Flask repeats validation independently; client-side checks are not a substitute for server-side checks.

## 3. Field contract

| Form name | Type / parsing | Required behavior | Server rule |
|---|---|---|---|
| `age` | Integer | Required | 1–130 inclusive |
| `sex` | Category string | Required | Values are populated from CSV in the browser |
| `weight` | Optional float | Both weight and height or neither | Finite and `0 < weight <= 300` kg |
| `height` | Optional float | Both height and weight or neither | Finite and `50 <= height <= 250` cm |
| `bmi` | Float | Required when no weight/height pair is supplied | Finite and `0 < bmi <= 53.1` |
| `children` | Integer | Optional; empty becomes 0 | 0–10 inclusive |
| `smoker` | Category string | Required | Values are populated from CSV in the browser |
| `region` | Category string | Required | Values are populated from CSV in the browser |

The server validates numeric fields and ranges. Current code does not explicitly check that posted categorical strings belong to the CSV options; normal browser use selects from the populated dropdowns.

## 4. Error handling

Expected user-input errors use HTTP 400 with a specific message. Examples include invalid age, incomplete height/weight, non-positive values, out-of-range BMI, and invalid child counts. The browser displays non-2xx response text with an `Error:` prefix.

## 5. Model and feature compatibility

The feature names and order passed to the DataFrame must remain aligned with the trained pipeline. The serialized model was created with scikit-learn 1.2.0; changing the runtime version may make pickle loading incompatible. Treat the pickle as a trusted deployment artifact only.

## 6. Local test cases

| Scenario | Expected result |
|---|---|
| Valid manual BMI and required fields | HTTP 200 prediction |
| Valid weight and height with blank manual BMI | HTTP 200 prediction using calculated BMI |
| Only weight or only height supplied | HTTP 400 |
| Weight above 300 kg or height outside 50–250 cm | HTTP 400 |
| BMI above 53.1 or non-finite BMI | HTTP 400 |
| Blank children | Treated as 0 |
| Children is fractional or outside 0–10 | HTTP 400 |
| Age blank, fractional, or outside 1–130 | HTTP 400 |
