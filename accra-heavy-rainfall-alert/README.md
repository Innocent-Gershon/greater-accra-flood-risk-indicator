# Greater Accra heavy-rainfall risk indicator

A student capstone prototype (BSc Software Engineering, African Leadership University).
It estimates whether the next 10-day period in Greater Accra, Ghana, will have heavy rain,
and shows a Low, Typical or High band with the share of past periods that were followed by heavy rain.

**What it is not.** Heavy rain raises flood risk, but this tool predicts heavy rainfall, not floods.
No flood records were available, so heavy rain (a 10-day total above 58.4 mm) is a stand-in.
It works for the whole region, not for individual neighborhoods, and it is not an official warning system.

- Walkthrough video: [add link]
- Technical report: [add link]
- Live dashboard (if deployed): [add link]

## What is in this repository

| Path | What it holds |
|---|---|
| `app.py` | Streamlit dashboard (risk page, and an About, privacy and limits page) |
| `api/main.py` | FastAPI backend: `/health`, `/periods`, `/predict`, `/importances` |
| `floodrisk/` | Core logic: features, model wrapper, risk bands, explainer, service |
| `notebooks/01_eda_and_modeling.ipynb` | Data exploration, model comparison, risk bands, reality check |
| `models/` | `flood_model_v2.pkl` and `settings.json` (created by the notebook) |
| `data/processed/` | `model_features_v2.csv` (created by the notebook) |
| `tests/` | Unit tests and API tests |
| `docs/` | Data dictionary, scope alignment table, fairness note, test log, screenshots, diagrams |

## Technical requirements

- Python 3.12 or 3.13 (the pinned NumPy needs a recent Python; Python 3.9 will not work)
- Package versions are pinned in `requirements.txt` to match the Colab run that saved the model
- Tested on: [your operating system and browser versions]

## Set up

```bash
python3.12 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
```

Copy these three files from the notebook output (Google Drive) into the repo:

1. `flood_model_v2.pkl` into `models/`
2. `settings.json` into `models/`
3. `model_features_v2.csv` into `data/processed/`

## Run

```bash
pytest                              # run the tests
streamlit run app.py                # dashboard at http://localhost:8501
uvicorn api.main:app --reload       # API; interactive docs at http://127.0.0.1:8000/docs
```

## Data

The notebook uses the Humanitarian Data Exchange (HDX) dataset "Ghana: Rainfall Indicators at Subnational Level".
Download `gha-rainfall-subnat-full.csv` from the dataset page and put it in `data/raw/` (this folder is not committed).
Source, licence and attribution: [copy the exact text from the HDX dataset page].
See `docs/data_dictionary.md` for what each column means.

## Deployment plan

The dashboard is planned for Streamlit Community Cloud (free tier): connect this GitHub repository,
set `app.py` as the main file and choose Python 3.12 in the app settings. The model and data files are
committed so the app can load them. The API is run locally for the demonstration and is not deployed.
Streamlit usage statistics are switched off in `.streamlit/config.toml`.

## Limitations

See `docs/fairness_and_limitations.md`. In short: the target is a stand-in for floods, the data is a
region-wide satellite average, heavy periods are few, the model beats a calendar-only lookup only by a small
margin, and the risk bands mostly follow the season.

## Scope changes from the approved proposal

See `docs/scope_alignment.md`.

## Licence and credits

Own code licence: [choose one and add a LICENSE file]. Third-party packages and data: see `THIRD_PARTY.md`.

## Author

[Innocent Nangah], [i.nangah@alustudent.com]. Supervisor: [
Elvira Immaculate Khwatenge].
