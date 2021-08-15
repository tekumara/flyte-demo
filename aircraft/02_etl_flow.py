from typing import Dict, List

import pandas as pd
from flytekit import task, workflow
from flytekit.types.schema import FlyteSchema

import aircraftlib as aclib
from aircraftlib.analysis import FIELDS_OF_INTEREST
from aircraftlib.openflights import OpenFlightsData
from aircraftlib.opensky import OPEN_SKY_FIELDS

aircraft_schema = FlyteSchema[OPEN_SKY_FIELDS]
cleaned_fields = FIELDS_OF_INTEREST.copy()
cleaned_fields.update({"airline": str})
cleaned_schema = FlyteSchema[cleaned_fields]


@task()
def extract_reference_data() -> OpenFlightsData:
    print("fetching reference data...")
    return aclib.fetch_reference_data()


@task()
def extract_live_data() -> aircraft_schema:
    # Get the live aircraft vector data around Dulles airport
    dulles_airport_position = aclib.Position(lat=38.9519444444, long=-77.4480555556)
    area_surrounding_dulles = aclib.bounding_box(dulles_airport_position, radius_km=200)

    print("fetching live aircraft data...")
    raw_aircraft_data = aclib.fetch_live_aircraft_data(area=area_surrounding_dulles)

    return pd.DataFrame(raw_aircraft_data, columns=OPEN_SKY_FIELDS)


@task()
def transform(raw_aircraft_data: aircraft_schema, airlines: Dict[str, str]) -> cleaned_schema:
    print("cleaning & transform aircraft data...")

    live_aircraft_data = []
    df = raw_aircraft_data.open().all()
    for _, raw_vector in df.iterrows():
        vector = aclib.clean_vector(raw_vector)
        if vector:
            aclib.add_airline_info(vector, airlines)
            live_aircraft_data.append(vector)

    return pd.DataFrame(live_aircraft_data, columns=cleaned_fields)


@task()
def load_reference_data(
    routes: List[Dict[str, str]], airlines: Dict[str, str], airports: Dict[str, Dict[str, str]]
) -> None:
    print("saving reference data...")
    db = aclib.Database()
    db.update_reference_data(OpenFlightsData(routes, airlines, airports))


@task()
def load_live_data(live_aircraft_data: cleaned_schema) -> None:
    print("saving live aircraft data...")
    db = aclib.Database()
    df = live_aircraft_data.open().all()
    rows = df.to_dict(orient="records")
    db.add_live_aircraft_data(rows)


@workflow()
def main() -> None:
    reference_data = extract_reference_data()
    live_data = extract_live_data()

    transformed_live_data = transform(raw_aircraft_data=live_data, airlines=reference_data.airlines)

    load_reference_data(
        routes=reference_data.routes, airlines=reference_data.airlines, airports=reference_data.airports
    )
    load_live_data(live_aircraft_data=transformed_live_data)


if __name__ == "__main__":
    main()
