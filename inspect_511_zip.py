import zipfile

zip_path = "data/511_2025_03_so.zip"

with zipfile.ZipFile(zip_path, "r") as z:
    files = z.namelist()

print("Number of files:", len(files))
print("\nFiles inside ZIP:\n")

for file in files:
    print(file)