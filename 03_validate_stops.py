import zipfile
import pandas as pd

zip_path = "data/511_2025_03_so.zip"

with zipfile.ZipFile(zip_path, "r") as z:

    stops = pd.read_csv(
        z.open("stops.txt"),
        usecols=[
            "stop_id",
            "stop_name",
            "stop_lat",
            "stop_lon"
        ]
    )

print("=" * 60)
print("STOPS VALIDATION")
print("=" * 60)

print("Rows:", len(stops))
print("Unique stops:", stops["stop_id"].nunique())

print("\nMissing values:")
print(stops.isna().sum())

print("\nSample:")
print(stops.head(10))