import zipfile
import pandas as pd

zip_path = "data/511_2025_03_so.zip"

with zipfile.ZipFile(zip_path, "r") as z:

    trips = pd.read_csv(
        z.open("trips.txt"),
        usecols=[
            "route_id",
            "service_id",
            "trip_id",
            "direction_id"
        ]
    )

print("=" * 60)
print("TRIPS VALIDATION")
print("=" * 60)

print("Rows:", len(trips))
print("Unique trips:", trips["trip_id"].nunique())
print("Unique routes:", trips["route_id"].nunique())
print("Unique services:", trips["service_id"].nunique())

print("\nMissing values:")
print(trips.isna().sum())

print("\nSample:")
print(trips.head())

print("\nTrips per route:")
print(
    trips.groupby("route_id")
         .size()
         .sort_values(ascending=False)
         .head(10)
)