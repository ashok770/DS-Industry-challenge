import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("511_API_KEY")

if not api_key:
    raise ValueError("511_API_KEY not found in .env")

url = (
    "https://api.511.org/transit/datafeeds"
    f"?api_key={api_key}"
    "&operator_id=RG"
    "&historic=2025-03-so"
)

output_file = "data/511_2025_03_so.zip"

print("Connecting to 511...")

response = requests.get(url, stream=True)

print("Status code:", response.status_code)

if response.status_code != 200:
    print(response.text)
    raise SystemExit("Download failed.")

total_size = int(response.headers.get("content-length", 0))

print(f"Total size: {total_size / (1024 * 1024):.2f} MB")

downloaded = 0
chunk_size = 1024 * 1024  # 1 MB

with open(output_file, "wb") as f:

    for chunk in response.iter_content(chunk_size=chunk_size):

        if chunk:
            f.write(chunk)
            downloaded += len(chunk)

            if total_size:
                percent = downloaded / total_size * 100

                print(
                    f"\rDownloaded: {downloaded / (1024 * 1024):.2f} MB "
                    f"({percent:.1f}%)",
                    end="",
                    flush=True
                )

            else:
                print(
                    f"\rDownloaded: {downloaded / (1024 * 1024):.2f} MB",
                    end="",
                    flush=True
                )

print("\n\nDownload completed!")
print("Saved to:", output_file)