from collections import OrderedDict
from typing import Any, Dict, List, Optional

from .opensky import AIRCRAFT_VECTOR_FIELDS

FIELDS_OF_INTEREST = OrderedDict(
    {
        "icao": str,
        "callsign": str,
        "time_position": int,
        "last_contact": int,
        "longitude": float,
        "latitude": float,
        "baro_altitude": float,
        "on_ground": bool,
        "velocity": float,
        "true_track": float,
        "vertical_rate": float,
        "geo_altitude": float,
    }
)


def clean_vector(raw_vector: List[Any]) -> Optional[Dict[str, Any]]:
    clean: Dict[str, Any] = dict(zip(AIRCRAFT_VECTOR_FIELDS, raw_vector[:], strict=True))

    if None in (clean["longitude"], clean["latitude"]):
        # this is an invalid vector, ignore it
        return None

    return {key: clean[key] for key in FIELDS_OF_INTEREST}


def add_airline_info(vector: Dict[str, Any], airlines: Dict[str, str]) -> None:
    airline = None
    callsign = vector["callsign"]

    if callsign:
        if callsign[:3] in airlines.keys():
            airline = callsign[:3]
        elif callsign[:2] in airlines.keys():
            airline = callsign[:2]

    vector["airline"] = airline
