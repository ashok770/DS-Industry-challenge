import zipfile
import csv

zip_path = "data/511_2025_03_so.zip"

target_trip = "AC:-1596408292"

print("=" * 60)
print("LIGHTWEIGHT TRIP MATCH TEST")
print("=" * 60)

observed_rows = []
scheduled_rows = []


# --------------------------------------------------
# 1. Read observations line-by-line
# --------------------------------------------------

print("\nSearching stop_observations.txt...")

with zipfile.ZipFile(zip_path, "r") as z:

    with z.open("stop_observations.txt") as f:

        reader = csv.DictReader(
            (line.decode("utf-8") for line in f)
        )

        for row in reader:

            if row["trip_id"] == target_trip:
                observed_rows.append(row)


print("Observed rows found:", len(observed_rows))


# --------------------------------------------------
# 2. Read stop_times line-by-line
# --------------------------------------------------

print("\nSearching stop_times.txt...")

with zipfile.ZipFile(zip_path, "r") as z:

    with z.open("stop_times.txt") as f:

        reader = csv.DictReader(
            (line.decode("utf-8") for line in f)
        )

        for row in reader:

            if row["trip_id"] == target_trip:
                scheduled_rows.append(row)


print("Scheduled rows found:", len(scheduled_rows))


# --------------------------------------------------
# 3. Display results
# --------------------------------------------------

print("\n" + "=" * 60)
print("OBSERVED DATA")
print("=" * 60)

for row in observed_rows:

    print(
        row["stop_sequence"],
        "| actual:",
        row["observed_arrival_time"],
        "| route:",
        row["route_id"]
    )


print("\n" + "=" * 60)
print("SCHEDULED DATA")
print("=" * 60)

for row in scheduled_rows:

    print(
        row["stop_sequence"],
        "| scheduled:",
        row["arrival_time"],
        "| distance:",
        row["shape_dist_traveled"]
    )