# Testing log

Paste real results only. Leave a cell as "not done" if you did not do it.

## Strategy 1: unit tests (`tests/`)

- Why: the date logic, lag features and risk bands must be exactly right, and a mistake would be silent.
- How: `pytest`, using a small model and small data files built in `tests/conftest.py`.
- Result: [paste the pytest summary line, for example "N passed"]
- Improvements made afterwards: [what you changed because of a failure, or "none needed"]

## Strategy 2: API integration tests (`tests/test_api.py`)

- Why: the API must answer correctly and reject bad input.
- How: FastAPI's test client, checking `/health`, `/periods`, `/predict` and `/importances`, including a missing period (404) and a bad date (422).
- Result: [paste the results]

## Manual checks

| Check | How | Result |
|---|---|---|
| Dashboard loads with the real model | `streamlit run app.py` | [ ] |
| Missing model file shows a clear message | Rename `models/flood_model_v2.pkl` and reload | [ ] |
| Phone layout | Open the app on a phone and screenshot | [ ] |
| Browsers | Chrome, [another browser], versions | [ ] |
| Load time | Time from opening to first result | [ ] |
| Operating systems | [which ones you used] | [ ] |
