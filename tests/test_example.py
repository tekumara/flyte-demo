from aircraft.etl_flow import extract_live_data, extract_reference_data


def test_extract_live_data():
    data_flyte_schema = extract_live_data()
    df = data_flyte_schema.open().all()

    assert len(df) == 17
    assert df["callsign"][0] == "SKQ74   "


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
