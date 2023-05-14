from typing import Annotated, Dict, List

import pandas as pd
from flytekit import task, workflow

import aircraftlib as aclib
from aircraftlib.analysis import FIELDS_OF_INTEREST
from aircraftlib.openflights import OpenFlightsData
from aircraftlib.opensky import OPEN_SKY_FIELDS

CLEANED_AIRCRAFT_FIELDS = FIELDS_OF_INTEREST.copy() | {"airline": str}
CLEANED_AIRCRAFT_COLS = list(CLEANED_AIRCRAFT_FIELDS.keys())

# Dataframes are stored as a StructuredDataset type, and persisted as parquet.
# The annotations define the column names and types, and are visible in the console.
# When the workflow is compiled during registration, input/output types of tasks
# will be checked and if the annotated columns differ a MismatchingTypes error is
# thrown. Pyright doesn't catch these differences in annotation, because the type
# is still just a Dataframe.
Aircraft = Annotated[pd.DataFrame, OPEN_SKY_FIELDS]
CleanedAircraft = Annotated[pd.DataFrame, CLEANED_AIRCRAFT_FIELDS]


@task()
def extract_reference_data() -> OpenFlightsData:
    print("fetching reference data...")
    return aclib.fetch_reference_data()


@task()
def extract_live_data() -> Aircraft:
    # Get the live aircraft vector data around Dulles airport
    dulles_airport_position = aclib.Position(lat=38.9519444444, long=-77.4480555556)
    area_surrounding_dulles = aclib.bounding_box(dulles_airport_position, radius_km=200)

    print("fetching live aircraft data...")
    raw_aircraft_data = aclib.fetch_live_aircraft_data(area=area_surrounding_dulles)

    return pd.DataFrame(raw_aircraft_data, columns=list(OPEN_SKY_FIELDS.keys()))


@task()
def transform(raw_aircraft_data: Aircraft, airlines: Dict[str, str]) -> CleanedAircraft:
    print("cleaning & transform aircraft data...")

    live_aircraft_data = []
    for _, raw_vector in raw_aircraft_data.iterrows():
        vector = aclib.clean_vector(raw_vector.to_list())
        if vector:
            aclib.add_airline_info(vector, airlines)
            live_aircraft_data.append(vector)

    return pd.DataFrame(live_aircraft_data, columns=CLEANED_AIRCRAFT_COLS)


@task()
def load_reference_data(
    routes: List[Dict[str, str]], airlines: Dict[str, str], airports: Dict[str, Dict[str, str]]
) -> None:
    print("saving reference data...")
    db = aclib.Database()
    db.update_reference_data(OpenFlightsData(routes, airlines, airports))


@task()
def load_live_data(live_aircraft_data: CleanedAircraft) -> None:
    print("saving live aircraft data...")
    db = aclib.Database()
    rows = live_aircraft_data.to_dict(orient="records")
    db.add_live_aircraft_data(rows)


@workflow
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
