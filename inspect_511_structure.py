import zipfile
import pandas as pd

zip_path = "data/511_2025_03_so.zip"

with zipfile.ZipFile(zip_path, "r") as z:

    for file in z.namelist():

        if not file.endswith(".txt"):
            continue

        print("\n" + "=" * 70)
        print(f"FILE: {file}")
        print("=" * 70)

        with z.open(file) as f:

            try:
                df = pd.read_csv(f, nrows=5)

                print("\nColumns:")
                print(list(df.columns))

                print("\nSample:")
                print(df.to_string(index=False))

            except Exception as e:
                print("Could not read file:", e)