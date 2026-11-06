# App Logic and Input Rules

**Prepared by: Rakesh Ranjan**

## Request flow

1. When a visitor opens `/`, Flask reads `clean_data.csv` and uses its distinct `sex`, `smoker`, and `region` values to populate the dropdown lists.
2. The visitor submits the form. JavaScript sends its values to `/predict` using an asynchronous POST request.
3. Flask validates and converts the inputs, creates a one-row pandas DataFrame in the feature order expected by the model, and calls `model.predict`.
4. A valid request returns the predicted premium. Invalid values return an explanatory message with HTTP status 400, which the page displays.

## Inputs and validation

| Input | Required? | Accepted value |
|---|---|---|
| Age | Yes | Whole number from 1 to 130 |
| Sex | Yes | Option populated from `clean_data.csv` |
| Weight | Optional | If supplied, must be finite, greater than 0, and no more than 300 kg |
| Height | Optional | If supplied, must be finite and between 50 and 250 cm; 50 cm is an application input floor, not a medical standard |
| BMI | Yes, unless calculated from weight and height | Finite number greater than 0 and no more than 53.1 |
| Children | No | Blank means 0; otherwise a whole number from 0 to 10 |
| Smoker | Yes | Option populated from `clean_data.csv` |
| Region | Yes | Option populated from `clean_data.csv` |

Age, BMI, and dropdowns are required for prediction. Weight and height are an optional alternative for supplying BMI: either provide both or leave both blank. Height must be between 50 and 250 cm; the 50 cm minimum is an application input floor, not a medical standard. If both measurements are provided, the browser displays a BMI rounded to one decimal place, while Flask computes BMI from the submitted values using the full precision:

`BMI = weight in kilograms / (height in meters × height in meters)`

When weight and height are blank, Flask uses the manually entered BMI. The BMI maximum of 53.1 is the largest BMI in the cleaned dataset and limits predictions to the model's observed BMI range. Weight and height limits are broad input sanity limits.

If BMI calculated from weight and height exceeds 53.1, the form and server ask the user to check height first and then verify weight if the height is correct. The BMI alone cannot determine which measurement was entered incorrectly. A manually entered BMI over the limit is reported as a BMI error.

Validation exists in the HTML/browser for immediate feedback and in Flask so requests are checked again on the server. The server-side checks are authoritative.

The form also displays an informational healthy-BMI reference based on age and the selected sex: CDC 5th-to-below-85th-percentile ranges for ages 2-19, and the adult 18.5-24.9 range from age 20. The pediatric figures are rounded estimates at each completed year, so the exact percentile varies with age in months. This reference does not block or change predictions; BMI is still validated against the model data maximum of 53.1. The insurance model was trained on adult data, so estimates for anyone under 18 are outside its training population and should not be relied on. BMI-for-age references are not shown for children under 2.

The pediatric percentile values are derived from the [CDC BMI-for-age data](https://www.cdc.gov/growthcharts/data/zscore/bmiagerev.csv).

## Local environment setup

This project includes a small app-specific `requirements.txt` to avoid installing unrelated notebook and analysis packages. Create the environment outside a OneDrive-synced directory, install those requirements, and run `app.py` from this folder. The trained pickle records scikit-learn 1.2.0; loading it with a different scikit-learn version may fail or behave incompatibly.

Flask debug mode is disabled by default. To enable it only for local development in PowerShell, set `$env:FLASK_DEBUG = "1"` before running `app.py`; use `Remove-Item Env:FLASK_DEBUG` to unset it in that terminal session. Never enable Flask debug mode on a public or production server. Production deployments should use a production WSGI server with debug mode disabled.
