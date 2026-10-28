<!-- # Day 1 — API Data Analysis Using Python Structures

## Project overview

This project retrieves JSON records from the JSONPlaceholder `/users` API, explores their nested structure, extracts customer attributes, aggregates customers by city and email domain using plain Python and then validates the city counts with pandas. It exports two CSV files and a chart for a presentation.


## Project structure

day1-api-analysis/
├── analysis.py
├── output/
│   ├── customers.csv
│   ├── city_counts.csv
│   └── customer_distribution.png
├── requirements.txt
└── README.md
```

## How to run

Use Python 3.10 or later.

1. Open a terminal in this project directory.
2. It is recommended to create and activate a virtual environment:
   - Windows: `py -m venv .venv` then `.venv\\Scripts\\activate`
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Run the analysis:

   ```bash
   python analysis.py
   ```

The script makes a live API request with a 10-second timeout. It checks the HTTP status, parses JSON and prints a clear error message if the request fails. If the API is unavailable, it stops rather than writing misleading empty results.

## Nested structure exploration

The explore() function recursively prints each dictionary key and its Python type. Nested dictionaries and lists are traversed with indentation to show depth.

Key nested attributes in each user record:

- address is a dictionary containing 'street', 'suite', 'city', 'zipcode', and 'geo'.
- address.geo is a dictionary containing 'lat' and 'lng'. These are the deepest location attributes: 'customer["address"]["geo"]["lat"]' and 'customer["address"]["geo"]["lng"]'.
- company is a dictionary containing 'name', 'catchPhrase', and 'bs'.
- address and company are reached from the top-level customer dictionary; geo is reached through address.

## Approach

1. **Retrieve:** `get_customers()` uses `requests.get(..., timeout=10)`, `raise_for_status()`, and `.json()`, with request and JSON errors handled.
2. **Explore:** `explore()` recursively visits dictionaries and lists and prints each key/index with its type.
3. **Flatten:** `extract_attributes()` selects the requested fields and extracts the email domain. Latitude and longitude are converted to floats.
4. **Unique cities:** `unique_cities()` uses a set comprehension.
5. **Count without pandas:** `city_counts()` uses a dictionary and loop; `email_domain_counts()` uses a dictionary comprehension.
6. **Validate with pandas:** `to_dataframe()` creates a DataFrame, and `value_counts()` is compared with the plain-Python city counts.
7. **Export and chart:** the script writes CSV files without a pandas index and saves a labelled bar chart.

## Findings

1. Run python analysis.py to print the findings for the live response. In the standard JSONPlaceholder sample, there are 10 user records and 10 distinct cities so every city has one sample user. That means city counts alone do not show a concentration in any one city.

2. The email top level domain chart is more useful than a city chart for this particular sample because it groups records into a smaller set of repeated categories, the city chart has one-count bars for every city. Email suffixes are only descriptive and should not be treated as a reliable proxy for customer region or marketing eligibility.

## Assumptions and limitations

- The API's id is exported as customer_id to make the CSV column's meaning clear.
- email_domain is the final suffix after the last dot (for example, biz, tv, or net), following the starter function’s top level domain wording.
- latitude and longitude are floats. Missing coordinates become NaN.
- City counts are sorted by descending count, then city name alphabetically for ties.
- Email domain counts are sorted by descending count, then domain alphabetically for display.
- The endpoint is public sample data. Do not use these records to make real customer, regional or campaign decisions.
