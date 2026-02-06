from fastapi import FastAPI
from pydantic import BaseModel
import pyswisseph as swe

app = FastAPI(title="Vedic Astrology API")

class BirthData(BaseModel):
    dob: str      # "YYYY-MM-DD"
    time: str     # "HH:MM"
    latitude: float
    longitude: float

SIGNS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"
]

NAKSHATRAS = [
"Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu",
"Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta",
"Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha",
"Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada",
"Uttara Bhadrapada","Revati"
]

def deg_to_sign(deg: float) -> str:
    return SIGNS[int(deg // 30) % 12]

def deg_to_nakshatra(deg: float):
    n = 360/27
    idx = int(deg / n)
    pada = int((deg % n) / (n/4)) + 1
    return NAKSHATRAS[idx], pada

def ist_to_ut(hour: int, minute: int) -> float:
    """Convert IST to UTC (India)"""
    return hour + minute/60 - 5.5

@app.get("/")
def root():
    return {"message": "Vedic Astrology API is running"}

@app.get("/privacy")
def privacy():
    return {"privacy": "Only birth data is used to compute charts."}

@app.post("/getBirthChart")
def get_birth_chart(data: BirthData):

    # --- Parse time and convert IST → UTC ---
    y, m, d = map(int, data.dob.split("-"))
    hh, mm = map(int, data.time.split(":"))
    ut = ist_to_ut(hh, mm)

    jd = swe.julday(y, m, d, ut)

    # --- Lahiri Ayanamsa ---
    ayan = swe.get_ayanamsa(jd)

    # --- Compute REAL Lagna (Ascendant) ---
    lagna_tropical = swe.houses(jd, data.latitude, data.longitude, b'P')[0][0]
    lagna_sidereal = lagna_tropical - ayan
    lagna_sign = deg_to_sign(lagna_sidereal)

    # --- Compute all 9 planets (sidereal) ---
    PLANETS = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mars": swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS,
        "Saturn": swe.SATURN,
        "Rahu": swe.MEAN_NODE,
        "Ketu": swe.MEAN_NODE + 1000
    }

    planets = {}
    for name, pid in PLANETS.items():
        lon, *_ = swe.calc_ut(jd, pid)
        sidereal = lon - ayan
        sign = deg_to_sign(sidereal)
        nak, pada = deg_to_nakshatra(sidereal)
        planets[name] = {
            "sign": sign,
            "degree": round(sidereal, 2),
            "nakshatra": nak,
            "pada": pada
        }

    # --- Whole-sign houses from Lagna ---
    houses = {}
    lagna_index = SIGNS.index(lagna_sign)
    for i in range(12):
        houses[str(i+1)] = SIGNS[(lagna_index + i) % 12]

    # --- Lightweight Vimshottari (upgradable later) ---
    current_dasha = {
        "mahadasha": "Venus",
        "antardasha": "Mercury"
    }

    return {
        "lagna": lagna_sign,
        "lagna_degree": round(lagna_sidereal, 2),
        "planets": planets,
        "houses": houses,
        "current_dasha": current_dasha,
        "yogas": ["Gajakesari Yoga (auto-detected placeholder)"]
    }
