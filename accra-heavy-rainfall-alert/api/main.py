"""Small web API that serves the same predictions as the dashboard."""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from floodrisk import __version__
from floodrisk.service import PeriodNotFoundError, PredictionService

NOTE = (
    "Estimates heavy rainfall in the next 10-day period. It does not detect floods. "
    "raw_score is not a probability: use past_heavy_rain_rate instead."
)


class PredictionResponse(BaseModel):
    """What /predict returns."""

    made_on: date
    for_period_start: date
    risk_band: str
    past_heavy_rain_rate: float
    raw_score: float
    followed_by_heavy_rain: Optional[bool]
    inputs: dict
    note: str


def create_app(service: Optional[PredictionService] = None) -> FastAPI:
    """Build the API. A ready-made service can be passed in (the tests do this)."""
    app = FastAPI(
        title="Greater Accra heavy-rainfall indicator API",
        version=__version__,
        description="Heavy rain raises flood risk. This API estimates heavy rainfall, not floods.",
    )
    state = {"service": service}

    def get_service() -> PredictionService:
        """Load the model files on first use and report a missing file as a 503 error."""
        if state["service"] is None:
            try:
                state["service"] = PredictionService.from_files()
            except FileNotFoundError as error:
                raise HTTPException(status_code=503, detail=str(error)) from error
        return state["service"]

    @app.get("/health")
    def health(svc: PredictionService = Depends(get_service)) -> dict:
        """Check that the model and data are loaded."""
        return {"status": "ok", "version": __version__, "periods": len(svc.available_periods())}

    @app.get("/periods")
    def periods(svc: PredictionService = Depends(get_service)) -> dict:
        """First and last date a forecast can be made from."""
        first, last = svc.data_range()
        return {"first": first, "last": last, "count": len(svc.available_periods())}

    @app.get("/predict", response_model=PredictionResponse)
    def predict(period: date, svc: PredictionService = Depends(get_service)) -> PredictionResponse:
        """Risk band and past rate for the 10-day period after the given period start."""
        try:
            result = svc.predict_for(period)
        except PeriodNotFoundError as error:
            raise HTTPException(status_code=404, detail=str(error)) from error
        prediction = result.prediction
        return PredictionResponse(
            made_on=prediction.made_on,
            for_period_start=prediction.for_period_start,
            risk_band=prediction.level.value,
            past_heavy_rain_rate=prediction.past_heavy_rate,
            raw_score=prediction.raw_score,
            followed_by_heavy_rain=result.followed_by_heavy_rain,
            inputs=result.inputs,
            note=NOTE,
        )

    @app.get("/importances")
    def importances(svc: PredictionService = Depends(get_service)) -> list:
        """How much the model relies on each input."""
        table = svc.importances()
        return [
            {"input": row.input, "label": row.label, "share": float(row.share)}
            for row in table.itertuples()
        ]

    return app


# The app that uvicorn runs: uvicorn api.main:app
app = create_app()
