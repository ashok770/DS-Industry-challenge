import zipfile
import pandas as pd

zip_path = "data/511_2025_03_so.zip"

with zipfile.ZipFile(zip_path, "r") as z:

    stop_times = pd.read_csv(
        z.open("stop_times.txt"),
        nrows=50_000,
        usecols=[
            "trip_id",
            "stop_id",
            "stop_sequence",
            "arrival_time",
            "departure_time",
            "shape_dist_traveled",
            "timepoint"
        ]
    )

print("=" * 60)
print("STOP TIMES INSPECTION")
print("=" * 60)

print("Rows loaded:", len(stop_times))

print("\nColumns:")
print(list(stop_times.columns))

print("\nMissing values:")
print(stop_times.isna().sum())

print("\nUnique trips in sample:",
      stop_times["trip_id"].nunique())

print("\nSample:")
print(stop_times.head(15).to_string(index=False))

print("\nTimepoint distribution:")
print(stop_times["timepoint"].value_counts(dropna=False))

print("\nDistance statistics:")
print(stop_times["shape_dist_traveled"].describe())