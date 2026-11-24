"""Greater Accra heavy-rainfall risk indicator (Streamlit dashboard)."""
import pandas as pd
import streamlit as st

from floodrisk import config
from floodrisk.features import PLAIN_LABELS
from floodrisk.service import PredictionService

st.set_page_config(page_title="Greater Accra heavy-rainfall indicator", layout="centered")

NOTICE = (
    "This tool estimates the chance of heavy rain in the next 10-day period. "
    "Heavy rain raises flood risk, but this tool does not detect floods. "
    "Always check official NADMO and GMet warnings."
)


@st.cache_resource
def load_service() -> PredictionService:
    """Load the model, settings and feature table once."""
    return PredictionService.from_files()


def format_period(day) -> str:
    """Readable label for a period in the drop-down list."""
    return day.strftime("%d %B %Y")


def render_risk_tab(service: PredictionService) -> None:
    """The main page: choose a period and read the band."""


    periods = list(reversed(service.available_periods()))   # newest first
    chosen = st.selectbox(
        "Make the forecast from this 10-day period",
        periods,
        format_func=format_period,
    )
    result = service.predict_for(chosen)
    prediction = result.prediction

    st.write(f"Forecast for the 10-day period starting {prediction.for_period_start:%d %B %Y}.")

    left, right = st.columns(2)
    left.metric("Risk band", prediction.level.value)
    right.metric("Heavy rain followed in the past", f"{prediction.past_heavy_rate:.1%}")

    st.write(
        f"In past data, heavy rain (more than {service.heavy_rain_cutoff_mm:.1f} mm in 10 days) "
        f"followed about {prediction.past_heavy_rate:.1%} of periods rated {prediction.level.value}. "
        "This is what happened before. It is not a probability for the next period."
    )
    base_rate = service.base_rate()
    if base_rate is not None:
        st.write(f"For comparison, heavy rain followed {base_rate:.1%} of all periods in the data.")

    if result.followed_by_heavy_rain is not None:
        outcome = "did" if result.followed_by_heavy_rain else "did not"
        st.info(f"What actually happened: heavy rain {outcome} follow this period.")

    with st.expander("Show details"):
        st.write("Inputs the model used for this period")
        table = pd.DataFrame(
            {
                "Input": [PLAIN_LABELS.get(name, name) for name in result.inputs],
                "Value": [round(value, 2) for value in result.inputs.values()],
            }
        )
        st.dataframe(table, hide_index=True)
        st.write("How much the model relies on each input. This shows what the model uses, not what causes heavy rain.")
        st.bar_chart(service.importances().set_index("label")["share"])


def render_about_tab(service: PredictionService) -> None:
    """Privacy policy, limits and sources. Every statement here can be checked in the code."""
    first, last = service.data_range()
    st.header("About, privacy and limits")

    st.subheader("Limits")
    st.write(
        "The tool does not detect floods, and heavy rain is only one cause of flooding. Drainage and planning "
        "also matter. It uses a region-wide average, so it cannot show local conditions in a neighborhood. "
        "In tests over five time windows, the model beat a calendar-only lookup by a small margin "
        "(average PR-AUC 0.392 against 0.331), and the bands mostly follow the season. "
        "For past dates, the model has already seen those periods in training, so their bands look "
        "better than future forecasts would. The fair tests are in the project notebook. "
        "A Low band does not mean safe. Two of four documented Accra floods were rated High. "
        "Residents are not direct users: the tool was built for disaster management officials."
    )

    st.subheader("Data and method")
    st.write(
        f"The tool uses 10-day rainfall figures for the whole Greater Accra region, from "
        f"{first:%d %B %Y} to {last:%d %B %Y}, published on the Humanitarian Data Exchange. "
        f"No flood records were available, so heavy rain (more than {service.heavy_rain_cutoff_mm:.1f} mm "
        "in 10 days) is used as a stand-in. A Random Forest model rates each period Low, Typical or High. "
        "The percentage shown is how often heavy rain really followed that band in the past."
    )
    st.write(f"Data source and licence: {config.DATA_ATTRIBUTION}")

    st.subheader("How often it updates")
    st.write(
        "The data are published in 10-day periods. This prototype does not update itself and does not "
        f"use a live feed. Its latest forecast date is {last:%d %B %Y}."
    )

    st.subheader("Privacy")
    st.write(
        "This app does not ask for, store or send personal information. There is no login. "
        "The app's own code sets no cookies. Usage statistics are switched off in the app's settings file. "
        "The hosting service may keep standard technical logs that this app cannot control."
    )

    st.subheader("Limits")
    st.write(
        "The tool does not detect floods, and heavy rain is only one cause of flooding. Drainage and planning "
        "also matter. It uses a region-wide average, so it cannot show local conditions in a neighborhood. "
        "In tests over five time windows, the model beat a calendar-only lookup by a small margin "
        "(average PR-AUC 0.392 against 0.331), and the bands mostly follow the season. "
        "A Low band does not mean safe. Two of four documented Accra floods were rated High. "
        "Residents are not direct users: the tool was built for disaster management officials."
    )

    st.subheader("Contact")
    st.write(config.CONTACT_EMAIL)


try:
    service = load_service()
except FileNotFoundError as error:
    st.error(f"The app cannot start because a file is missing. {error}")
    st.stop()

st.title("Heavy-rainfall risk indicator for Greater Accra")
st.warning(NOTICE)

risk_tab, about_tab = st.tabs(["Risk for a period", "About, privacy and limits"])
with risk_tab:
    render_risk_tab(service)
with about_tab:
    render_about_tab(service)
