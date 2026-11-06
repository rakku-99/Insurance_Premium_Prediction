# Architecture Design Document

**Project:** Insurance Premium Prediction App  
**Prepared by:** Rakesh Ranjan  
**Status:** Describes current local Flask application and design constraints

## 1. Architectural style

The current system is a small, single-process web application using a server-rendered Flask page and an HTTP prediction endpoint. The browser handles presentation and immediate validation feedback. Flask owns authoritative validation and prediction orchestration. A pre-trained scikit-learn artifact performs inference; there is no database or online training component.

## 2. Logical layers

```text
Presentation layer
  templates/index.html
  JavaScript form and BMI helper
  static/css/style.css
          |
          | GET / and POST /predict
          v
Application layer
  Flask routes in app.py
  parsing, validation, BMI derivation, response handling
          |
          +-----------------------+
          |                       |
          v                       v
Data/config inputs          Inference component
clean_data.csv              gradient_boosting_regressor_model.pkl
dropdown categories         sklearn model.predict(DataFrame)
```

## 3. Module responsibilities

### Presentation

- Renders age, gender, BMI, optional height and weight, children, smoker, and region controls.
- Uses HTML constraints for numeric range and required fields.
- Uses JavaScript to calculate BMI for display and submit the form asynchronously.
- Shows the prediction or server error in the result area.

### Flask request/application module

- Loads the trained model and dropdown data at process startup.
- Exposes `GET /` and `POST /predict`.
- Converts form strings into numeric values, enforces input rules, calculates BMI where appropriate, and assembles model features.
- Returns prediction text on success and a 400 response for invalid inputs.

### Model and reference data

- The pickled scikit-learn model is inference-only.
- `clean_data.csv` is used to create unique dropdown options for `sex`, `smoker`, and `region`.
- Inputs are passed in model feature order: age, sex, BMI, children, smoker, region.

## 4. Data flow and interfaces

### `GET /`

`Browser -> Flask index route -> clean_data.csv category values -> Jinja template -> HTML response`

### `POST /predict`

`Browser FormData -> Flask validation -> (optional) BMI calculation -> pandas DataFrame -> model.predict -> HTTP response -> browser result area`

The prediction endpoint expects these form field names: `age`, `sex`, `weight`, `height`, `bmi`, `children`, `smoker`, and `region`.

## 5. Runtime and deployment topology

### Current local topology

- One Python process runs the Flask development server on port 1947.
- The browser connects to the local server.
- CSV and model files are read from the application working directory.
- The model and dataset are loaded once when `app.py` is imported.

### Production considerations (not implemented)

- Run behind a production WSGI server and disable Flask debug mode.
- Configure model/data paths robustly rather than relying on the current working directory.
- Pin and test dependencies against the model's scikit-learn version.
- Add operational logging, health checks, and error monitoring.
- Protect any public endpoint with suitable request limits and deployment controls.
- Load only trusted pickle artifacts.

## 6. Input validation design

The browser gives immediate feedback, but request validation is repeated in Flask:

- Age: integer, 1–130.
- Weight/height: optional pair; weight finite and within `(0, 300]` kg, height finite and within `[50, 250]` cm. The 50 cm minimum is an application input floor, not a medical standard.
- BMI: finite and within `(0, 53.1]`; derived from weight/height if both supplied, otherwise read directly.
- Children: blank maps to 0; otherwise integer 0–10.
- Categorical dropdowns are sourced from the cleaned dataset for normal browser interaction.

BMI's maximum matches the cleaned data's observed maximum. The reviewed data has age values 18–64 and children values 0–5, while the app accepts broader ranges of 1–130 and 0–10. Predictions outside the training data's observed range may therefore be extrapolations and should be interpreted cautiously.

## 7. Dependencies and artifact compatibility

The app uses Flask, pandas, NumPy, and scikit-learn. The model pickle records scikit-learn 1.2.0. Loading scikit-learn pickle artifacts across versions is not guaranteed; the runtime should use the compatible pinned version. The local requirements file is intended for running the web app, not reproducing the original model training notebook.

## 8. Limitations and assumptions

- No user identity, sessions, storage, or prediction history.
- No database; category options are loaded from CSV.
- Model uncertainty or confidence intervals are not shown.
- The premium output is a model estimate and does not replace an insurer's quote.
- The current file loading expects a trusted local model and CSV to exist.
- Debug mode in `app.py` is suitable only for local development.

## 9. Related documents

- [HLD](HLD.md) — system scope and high-level request flows.
- [LLD](LLD.md) — endpoint and validation details.
- [Wireframe](WIREFRAME.md) — current page layout and interaction states.
- [App logic and setup](APP_LOGIC_AND_SETUP.md) — user-facing rules and local setup.
