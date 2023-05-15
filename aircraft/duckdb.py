from dataclasses import dataclass
from typing import Dict, List

import flytekit
import matplotlib.pyplot as plt
import mpld3
import numpy as np
import pandas as pd
import pyarrow as pa
import vaex
from dataclasses_json import dataclass_json
from flytekit import Resources, dynamic, kwtypes, task, workflow
from flytekit.types.structured.structured_dataset import StructuredDataset
from flytekitplugins.duckdb import DuckDBQuery

peak_hour_output = List[Dict[str, StructuredDataset]]
vaex_dfs_list = List[vaex.dataframe.DataFrameLocal]


@dataclass_json
@dataclass
class PeakOffPeak:
    year: int
    peak_hour: int
    off_peak_hour: int


pickup_query = DuckDBQuery(
    name="pickup_query",
    query=[
        "install httpfs",
        "load httpfs",
        """select hour(lpep_pickup_datetime) as hour,
        count(*) as count
        from read_parquet(?)
        group by hour""",
    ],
    inputs=kwtypes(params=List[str]),
)

dropoff_query = DuckDBQuery(
    name="dropoff_query",
    query=[
        "install httpfs",
        "load httpfs",
        """
        select hour(lpep_dropoff_datetime) as hour,
        count(*) as count
        from read_parquet(?)
        group by hour
        """,
    ],
    inputs=kwtypes(params=List[str]),
)

peak_hour_query = DuckDBQuery(
    name="peak_hour_query",
    query="""select hour
        from arrow_table
        where pickup_count + dropoff_count = (select max(pickup_count + dropoff_count)
                                                from arrow_table)""",
    inputs=kwtypes(arrow_table=pa.Table),
)

off_peak_hour_query = DuckDBQuery(
    name="off_peak_hour_query",
    query="""select hour
        from arrow_table
        where pickup_count + dropoff_count = (select min(pickup_count + dropoff_count)
                                                from arrow_table)""",
    inputs=kwtypes(arrow_table=pa.Table),
)


@dynamic(requests=Resources(mem="1Gi", cpu="2"))
def fetch_trips_data(years: List[int], months: List[int]) -> vaex_dfs_list:
    result = []
    for year in years:
        for month in months:
            url = f"https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_{year}-{month:02d}.parquet"
            pickup_sd = pickup_query(params=[url])
            dropoff_sd = dropoff_query(params=[url])
            result.append(
                {
                    "pickup_sd": pickup_sd,
                    "dropoff_sd": dropoff_sd,
                }
            )
    return coalesce_dfs(sds=result, years=years)


@task(requests=Resources(mem="500Mi", cpu="2"))
def coalesce_dfs(sds: peak_hour_output, years: List[int]) -> vaex_dfs_list:
    # add year to every dictionary
    partition_index = int(len(sds) / len(years))
    for index, item in enumerate(sds):
        item["year"] = years[index // partition_index]

    # sort by year
    sds.sort(key=lambda x: x["year"])

    result_list = []
    end_index = len(sds) / len(years)
    pickup_df, dropoff_df = None, None

    for index, item in enumerate(sds, start=1):
        materialized_pickup_df = item["pickup_sd"].open(vaex.dataframe.DataFrameLocal).all()
        materialized_dropoff_df = item["dropoff_sd"].open(vaex.dataframe.DataFrameLocal).all()
        pickup_df = vaex.concat([pickup_df, materialized_pickup_df]) if pickup_df else materialized_pickup_df
        dropoff_df = vaex.concat([dropoff_df, materialized_dropoff_df]) if dropoff_df else materialized_dropoff_df
        # for every year, store the number of pickups and dropoffs
        if index % end_index == 0:
            year = item["year"]
            pickup_df = pickup_df.groupby(by="hour").agg({"count": "sum"})
            dropoff_df = dropoff_df.groupby(by="hour").agg({"count": "sum"})
            pickup_df.rename("count", "pickup_count")
            dropoff_df.rename("count", "dropoff_count")
            result_df = pickup_df.join(dropoff_df, on="hour")
            result_df["year"] = np.array([year] * len(result_df))
            result_list.append(result_df)
            pickup_df, dropoff_df = None, None

    return result_list


@task(disable_deck=False)
def generate_plot(dfs: vaex_dfs_list):
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    for df in dfs:
        ax.plot(
            df.hour,
            df.pickup_count,
            label=f"{df.year.values[0]} Pickup Count",
            linestyle="--",
            marker="o",
        )
        ax.plot(
            df.hour,
            df.dropoff_count,
            label=f"{df.year.values[0]} Dropoff Count",
            linestyle="--",
            marker="o",
        )
    ax.set_xlabel("hour")
    ax.set_ylabel("count")
    ax.set_title("Number of pickups/dropoffs")
    ax.legend(loc="best")
    fig.savefig("plot.png")

    flytekit.Deck("matplotlib", mpld3.fig_to_html(fig))


@task
def peak_offpeak_postprocess(
    df: vaex.dataframe.DataFrameLocal,
    peak_hour_sd: StructuredDataset,
    off_peak_hour_sd: StructuredDataset,
) -> PeakOffPeak:
    peak_hour = peak_hour_sd.open(pd.DataFrame).all().iloc[0]["hour"].item()
    off_peak_hour = off_peak_hour_sd.open(pd.DataFrame).all().iloc[0]["hour"].item()

    return PeakOffPeak(df.year.values[0].as_py(), peak_hour, off_peak_hour)


@dynamic(requests=Resources(mem="500Mi", cpu="2"))
def peak_offpeak_hours(dfs: vaex_dfs_list) -> List[PeakOffPeak]:
    result = []
    for df in dfs:
        arrow_table = df.to_arrow_table()
        peak_hour_sd = peak_hour_query(arrow_table=arrow_table)
        off_peak_hour_sd = off_peak_hour_query(arrow_table=arrow_table)
        df_result = peak_offpeak_postprocess(
            df=df,
            peak_hour_sd=peak_hour_sd,
            off_peak_hour_sd=off_peak_hour_sd,
        )
        result.append(df_result)
    return result


@workflow
def duckdb_wf(years: List[int] = [2019, 2020, 2021, 2022], months: List[int] = list(range(1, 13))) -> List[PeakOffPeak]:
    result_dfs = fetch_trips_data(years=years, months=months)
    generate_plot(dfs=result_dfs)
    return peak_offpeak_hours(dfs=result_dfs)


if __name__ == "__main__":
    print(duckdb_wf())
