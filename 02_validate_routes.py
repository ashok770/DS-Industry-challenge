import zipfile
import pandas as pd

zip_path = "data/511_2025_03_so.zip"

with zipfile.ZipFile(zip_path, "r") as z:

    routes = pd.read_csv(
        z.open("routes.txt")
    )

print("=" * 60)
print("ROUTES VALIDATION")
print("=" * 60)

print("Rows:", len(routes))
print("Unique route IDs:", routes["route_id"].nunique())

print("\nColumns:")
print(list(routes.columns))

print("\nMissing values:")
print(routes.isna().sum())

print("\nSample:")
print(
    routes[
        [
            "route_id",
            "agency_id",
            "route_short_name",
            "route_long_name"
        ]
    ].head(10)
)