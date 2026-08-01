from pathlib import Path
import re

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRT_PATH = PROJECT_ROOT / "datasets" / "raw" / "DJI_0995.SRT"

if not SRT_PATH.exists():
    print(f"SRT file not found:\n{SRT_PATH}")
    exit()

text = SRT_PATH.read_text(
    encoding="utf-8",
    errors="ignore"
)

print("=" * 70)
print("DJI SRT INSPECTOR")
print("=" * 70)

print(f"\nFile : {SRT_PATH.name}")

print(f"File Size : {SRT_PATH.stat().st_size / 1024:.2f} KB")

frame_numbers = re.findall(
    r"SrtCnt\s*:\s*(\d+)",
    text
)

timestamps = re.findall(
    r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+",
    text
)

latitudes = re.findall(
    r"latitude:\s*([-\d.]+)",
    text
)

longitudes = re.findall(
    r"longitude:\s*([-\d.]+)",
    text
)

altitudes = re.findall(
    r"altitude:\s*([-\d.]+)",
    text
)

print("\nTelemetry Summary")
print("-" * 70)

print(f"Frames      : {len(frame_numbers)}")
print(f"Timestamps  : {len(timestamps)}")
print(f"Latitudes   : {len(latitudes)}")
print(f"Longitudes  : {len(longitudes)}")
print(f"Altitudes   : {len(altitudes)}")

if latitudes:

    print("\nGPS Range")

    print(
        f"Latitude  : {min(map(float,latitudes)):.6f}"
        f"  ->  {max(map(float,latitudes)):.6f}"
    )

    print(
        f"Longitude : {min(map(float,longitudes)):.6f}"
        f"  ->  {max(map(float,longitudes)):.6f}"
    )

    print(
        f"Altitude  : {min(map(float,altitudes)):.2f}"
        f"  ->  {max(map(float,altitudes)):.2f}"
    )

print("\nFirst Frame")

print("-" * 70)

print(text[:700])

print("\nInspection Complete")