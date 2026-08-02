from pathlib import Path
import re
import csv


class DJISRTParser:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.raw_dir = (
            self.project_root /
            "datasets" /
            "raw"
        )

        self.telemetry_dir = (
            self.project_root /
            "datasets" /
            "telemetry"
        )

        self.telemetry_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.srt_path = (
            self.raw_dir /
            "DJI_0995.SRT"
        )

        self.output_csv = (
            self.telemetry_dir /
            "telemetry.csv"
        )

        if not self.srt_path.exists():

            raise FileNotFoundError(
                self.srt_path
            )

        self.text = self.srt_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        self.rows = []

    # --------------------------------------------------

    def parse(self):

        print("=" * 70)
        print("Parsing DJI SRT")
        print("=" * 70)

        pattern = re.compile(

            r"SrtCnt\s*:\s*(\d+).*?"
            r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d+).*?"
            r"\[iso\s*:\s*(\d+)\].*?"
            r"\[shutter\s*:\s*([^\]]+)\].*?"
            r"\[fnum\s*:\s*(\d+)\].*?"
            r"\[ev\s*:\s*([-\d.]+)\].*?"
            r"\[ct\s*:\s*(\d+)\].*?"
            r"\[focal_len\s*:\s*(\d+)\].*?"
            r"\[dzoom_ratio:\s*(\d+).*?"
            r"\[latitude:\s*([-\d.]+)\].*?"
            r"\[longitude:\s*([-\d.]+)\].*?"
            r"\[altitude:\s*([-\d.]+)\]",

            re.DOTALL

        )

        matches = pattern.findall(
            self.text
        )

        print(
            f"Records Found : {len(matches)}"
        )

        for m in matches:

            frame = int(m[0])

            timestamp = m[1]

            iso = int(m[2])

            shutter = m[3]

            fnum = int(m[4])

            ev = float(m[5])

            color_temp = int(m[6])

            focal_len = int(m[7])

            zoom_ratio = int(m[8])

            latitude = float(m[9])

            longitude = float(m[10])

            altitude = float(m[11])

            self.rows.append(

                {
                    "frame": frame,
                    "timestamp": timestamp,
                    "latitude": latitude,
                    "longitude": longitude,
                    "altitude": altitude,
                    "iso": iso,
                    "shutter": shutter,
                    "fnum": fnum,
                    "ev": ev,
                    "color_temp": color_temp,
                    "focal_len": focal_len,
                    "zoom_ratio": zoom_ratio
                }

            )

    # --------------------------------------------------

    def save_csv(self):

        print()
        print("=" * 70)
        print("Saving telemetry.csv")
        print("=" * 70)

        columns = [
            "frame",
            "timestamp",
            "latitude",
            "longitude",
            "altitude",
            "iso",
            "shutter",
            "fnum",
            "ev",
            "color_temp",
            "focal_len",
            "zoom_ratio"
        ]

        with open(
            self.output_csv,
            "w",
            newline="",
            encoding="utf-8"
        ) as csvfile:

            writer = csv.DictWriter(
                csvfile,
                fieldnames=columns
            )

            writer.writeheader()

            writer.writerows(
                self.rows
            )

        print(
            f"Saved {len(self.rows)} rows."
        )

        print(
            f"Output : {self.output_csv}"
        )

    # --------------------------------------------------

    def statistics(self):

        print()
        print("=" * 70)
        print("Telemetry Statistics")
        print("=" * 70)

        if len(self.rows) == 0:

            print("No records found.")
            return

        latitudes = [
            r["latitude"]
            for r in self.rows
        ]

        longitudes = [
            r["longitude"]
            for r in self.rows
        ]

        altitudes = [
            r["altitude"]
            for r in self.rows
        ]

        print(f"Frames        : {len(self.rows)}")

        print(
            f"Latitude      : {min(latitudes):.6f}"
            f" -> {max(latitudes):.6f}"
        )

        print(
            f"Longitude     : {min(longitudes):.6f}"
            f" -> {max(longitudes):.6f}"
        )

        print(
            f"Altitude      : {min(altitudes):.2f}"
            f" -> {max(altitudes):.2f}"
        )

        print()
        print("First Record")
        print("-" * 70)

        first = self.rows[0]

        for key, value in first.items():

            print(
                f"{key:15}: {value}"
            )

        print()
        print("Last Record")
        print("-" * 70)

        last = self.rows[-1]

        for key, value in last.items():

            print(
                f"{key:15}: {value}"
            )

    # --------------------------------------------------

    def run(self):

        self.parse()

        self.save_csv()

        self.statistics()

        print()
        print("=" * 70)
        print("DJI SRT PARSING COMPLETED")
        print("=" * 70)

        print(f"Input SRT      : {self.srt_path}")
        print(f"Output CSV     : {self.output_csv}")
        print(f"Total Records  : {len(self.rows)}")

        if len(self.rows) > 0:

            print()
            print("✓ Telemetry CSV generated successfully.")

        else:

            print()
            print("✗ No telemetry records generated.")


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    parser = DJISRTParser()

    parser.run()