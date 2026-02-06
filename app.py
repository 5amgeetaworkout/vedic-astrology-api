
from fastapi import FastAPI
from pydantic import BaseModel
import pyswisseph as swe

app = FastAPI(title="Vedic Astrology API")

class BirthData(BaseModel):
    dob: str      # "YYYY-MM-DD"
    time: str     # "HH:MM"
    latitude: float
    longitude: float

@app.get("/")
def root():
    return {"status": "running"}

@app.get("/privacy")
def privacy():
    return {
        "policy": "This API only receives birth data (date, time, location) to compute astrological charts."
    }

@app.post("/getBirthChart")
def get_birth_chart(data: BirthData):

    # Parse date and time
    y, m, d = map(int, data.dob.split("-"))
    hh, mm = map(int, data.time.split(":"))
    ut = hh + mm/60

    jd = swe.julday(y, m, d, ut)

    # Example: compute Sun longitude (real calculation)
    sun_lon, _, _ = swe.calc_ut(jd, swe.SUN)

    # Placeholder structure that matches ChatGPT schema
    return {
        "lagna": "Scorpio",
        "planets": {
            "Sun": {
                "sign": "Leo",
                "degree": round(sun_lon, 2),
                "nakshatra": "Magha",
                "pada": 2
            }
        },
        "houses": {
            "1": "Scorpio",
            "2": "Sagittarius"
        },
        "current_dasha": {
            "mahadasa": "Venus",
            "antardasha": "Mercury"
        },
        "yogas": ["Gajakesari Yoga"]
    }
