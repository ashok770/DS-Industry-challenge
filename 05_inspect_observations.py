import zipfile
import pandas as pd

zip_path = "data/511_2025_03_so.zip"

with zipfile.ZipFile(zip_path, "r") as z:

    observations = pd.read_csv(
        z.open("stop_observations.txt"),
        nrows=50_000,
        usecols=[
            "trip_id",
            "service_date",
            "vehicle_id",
            "stop_sequence",
            "observed_arrival_time",
            "observed_departure_time",
            "uncertainty",
            "route_id",
            "agency_id",
            "direction_id",
            "from_stop_id",
            "to_stop_id",
            "scheduled_arrival_time",
            "scheduled_departure_time"
        ]
    )

print("=" * 60)
print("STOP OBSERVATIONS INSPECTION")
print("=" * 60)

print("Rows loaded:", len(observations))

print("\nColumns:")
print(list(observations.columns))

print("\nMissing values:")
print(observations.isna().sum())

print("\nUnique trips:")
print(observations["trip_id"].nunique())

print("\nUnique routes:")
print(observations["route_id"].nunique())

print("\nUnique vehicles:")
print(observations["vehicle_id"].nunique())

print("\nService dates:")
print(observations["service_date"].value_counts())

print("\nSample:")
print(
    observations.head(15).to_string(index=False)
)

print("\nStop sequence statistics:")
print(
    observations["stop_sequence"].describe()
)

print("\nObserved arrival examples:")
print(
    observations[
        [
            "trip_id",
            "stop_sequence",
            "observed_arrival_time",
            "scheduled_arrival_time"
        ]
    ].head(20).to_string(index=False)
)