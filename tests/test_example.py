import numpy as np
import pandas as pd

from aircraft.etl_flow import cleaned_fields, extract_live_data, extract_reference_data, transform


def test_extract_live_data():
    data_flyte_schema = extract_live_data()
    df = data_flyte_schema.open().all()

    assert len(df) == 15
    assert df["callsign"][0] == "SWG641  "


def test_extract_reference_data():
    data = extract_reference_data()
    assert len(data) == 3
    assert data.routes[0] == {
        "airline": "C7",
        "codeshare": "",
        "equipment": "EMB",
        "from": "MAO",
        "stops": "0",
        "to": "CIZ",
    }
    assert data.airlines["0B"] == "Blue Air"
    assert data.airports["AAA"] == {
        "airport-name": "Anaa                                    ",
        "latitude": "-17.3542",
        "longitude": "-145.4961",
    }


def test_transform() -> None:
    raw_aircraft_data = pd.DataFrame(
        {
            "icao24": "XYZ",
            "callsign": "AA",
            "origin_country": "United States",
            "time_position": 1,
            "last_contact": 2,
            "longitude": -12.34,
            "latitude": 45.67,
            "baro_altitude": 123.45,
            "on_ground": False,
            "velocity": 1.29,
            "true_track": 39.38,
            "vertical_rate": np.nan,
            "sensors": None,
            "geo_altitude": np.nan,
            "squawk": None,
            "spi": False,
            "position_source": 0,
        },
        index=[0],
    )

    airlines = {"AA": "American Airlines", "DL": "Delta Air Lines"}

    expected = pd.DataFrame(
        [
            {
                "icao": "XYZ",
                "callsign": "AA",
                "time_position": 1,
                "last_contact": 2,
                "longitude": -12.34,
                "latitude": 45.67,
                "baro_altitude": 123.45,
                "on_ground": False,
                "velocity": 1.29,
                "true_track": 39.38,
                "vertical_rate": np.nan,
                "geo_altitude": np.nan,
                "airline": "AA",
            }
        ],
        columns=cleaned_fields,
    )

    # flyte only supports keyword args when calling tasks
    actual = transform(raw_aircraft_data=raw_aircraft_data, airlines=airlines)

    pd.testing.assert_frame_equal(actual.open().all(), expected)
