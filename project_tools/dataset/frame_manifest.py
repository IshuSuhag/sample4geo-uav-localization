from pathlib import Path
import pandas as pd


class FrameManifestBuilder:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.telemetry_csv = (
            self.project_root /
            "datasets" /
            "telemetry" /
            "telemetry.csv"
        )

        self.frames_dir = (
            self.project_root /
            "datasets" /
            "frames"
        )

        self.manifest_dir = (
            self.project_root /
            "datasets" /
            "manifests"
        )

        self.manifest_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.output_csv = (
            self.manifest_dir /
            "frame_manifest.csv"
        )

        if not self.telemetry_csv.exists():

            raise FileNotFoundError(
                self.telemetry_csv
            )

        if not self.frames_dir.exists():

            raise FileNotFoundError(
                self.frames_dir
            )

        self.telemetry = pd.read_csv(
            self.telemetry_csv
        )

        self.frames = sorted(
            self.frames_dir.glob("*.jpg")
        )

    # --------------------------------------------------

    def prepare(self):

        print("=" * 70)
        print("FRAME MANIFEST BUILDER")
        print("=" * 70)

        print()

        print(
            f"Telemetry Rows : {len(self.telemetry)}"
        )

        print(
            f"Frame Images   : {len(self.frames)}"
        )

        self.total = min(
            len(self.telemetry),
            len(self.frames)
        )

        print(
            f"Matched Frames : {self.total}"
        )

        self.rows = []

    # --------------------------------------------------

    def build_manifest(self):

        print()
        print("=" * 70)
        print("Building Manifest")
        print("=" * 70)

        for i in range(self.total):

            telemetry = self.telemetry.iloc[i]

            image_path = self.frames[i]

            self.rows.append(

                {

                    "frame_id": int(
                        telemetry["frame"]
                    ),

                    "image_name":
                        image_path.name,

                    "image_path":
                        str(image_path),

                    "timestamp":
                        telemetry["timestamp"],

                    "latitude":
                        telemetry["latitude"],

                    "longitude":
                        telemetry["longitude"],

                    "altitude":
                        telemetry["altitude"],

                    "iso":
                        telemetry["iso"],

                    "shutter":
                        telemetry["shutter"],

                    "fnum":
                        telemetry["fnum"],

                    "ev":
                        telemetry["ev"],

                    "color_temp":
                        telemetry["color_temp"],

                    "focal_len":
                        telemetry["focal_len"],

                    "zoom_ratio":
                        telemetry["zoom_ratio"]

                }

            )

            if (
                (i + 1) == 1
                or
                (i + 1) % 500 == 0
                or
                (i + 1) == self.total
            ):

                progress = (
                    (i + 1) /
                    self.total
                ) * 100

                print(
                    f"{i+1:5d}/{self.total}"
                    f" ({progress:.1f}%)"
                )

    # --------------------------------------------------

    def save_manifest(self):

        print()
        print("=" * 70)
        print("Saving Manifest")
        print("=" * 70)

        manifest = pd.DataFrame(
            self.rows
        )

        manifest.to_csv(

            self.output_csv,

            index=False

        )

        print(
            f"Saved {len(manifest)} records."
        )

        print(
            f"Output : {self.output_csv}"
        )

    # --------------------------------------------------

    def verify(self):

        print()
        print("=" * 70)
        print("Verification")
        print("=" * 70)

        manifest = pd.read_csv(
            self.output_csv
        )

        print(
            f"Manifest Records : {len(manifest)}"
        )

        print()

        print("First Record")
        print("-" * 70)

        print(
            manifest.iloc[0]
        )

        print()

        print("Last Record")
        print("-" * 70)

        print(
            manifest.iloc[-1]
        )

        print()

        print("✓ Verification Passed")

    # --------------------------------------------------

    def summary(self):

        print()
        print("=" * 70)
        print("FRAME MANIFEST CREATED")
        print("=" * 70)

        print(
            f"Telemetry Records : {len(self.telemetry)}"
        )

        print(
            f"Frame Images      : {len(self.frames)}"
        )

        print(
            f"Matched Records   : {self.total}"
        )

        print(
            f"Output CSV        : {self.output_csv}"
        )

        if len(self.telemetry) != len(self.frames):

            print()
            print(
                "NOTE: Frame count and telemetry count differ."
            )

            print(
                f"Telemetry : {len(self.telemetry)}"
            )

            print(
                f"Frames    : {len(self.frames)}"
            )

            print(
                f"Using first {self.total} matched records."
            )

        print()
        print("=" * 70)
        print("S4G-1.4 COMPLETED")
        print("=" * 70)

    # --------------------------------------------------

    def run(self):

        self.prepare()

        self.build_manifest()

        self.save_manifest()

        self.verify()

        self.summary()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    builder = FrameManifestBuilder()

    builder.run()