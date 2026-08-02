from pathlib import Path
from datetime import datetime

import cv2
import pandas as pd
import numpy as np


class SyncedFrameExtractor:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        # --------------------------------------------------
        # Input Files
        # --------------------------------------------------

        self.video_path = (
            self.project_root /
            "datasets" /
            "raw" /
            "DJI_0995.MP4"
        )

        self.telemetry_path = (
            self.project_root /
            "datasets" /
            "telemetry" /
            "telemetry.csv"
        )

        # --------------------------------------------------
        # Output Locations
        # --------------------------------------------------

        self.frame_dir = (
            self.project_root /
            "datasets" /
            "frames" /
            "DJI_0995"
        )

        self.frame_dir.mkdir(
            parents=True,
            exist_ok=True
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

        self.manifest_path = (
            self.manifest_dir /
            "DJI_0995_frames.csv"
        )

        # --------------------------------------------------
        # Load Telemetry
        # --------------------------------------------------

        self.telemetry = pd.read_csv(
            self.telemetry_path
        )

        # --------------------------------------------------
        # Convert wall-clock timestamps
        # into elapsed milliseconds
        # --------------------------------------------------

        self.telemetry[
            "timestamp"
        ] = pd.to_datetime(
            self.telemetry["timestamp"],
            format="%Y-%m-%d %H:%M:%S,%f"
        )

        first_time = self.telemetry[
            "timestamp"
        ].iloc[0]

        self.telemetry[
            "elapsed_ms"
        ] = (

            self.telemetry["timestamp"]

            - first_time

        ).dt.total_seconds() * 1000

        # --------------------------------------------------
        # Open Video
        # --------------------------------------------------

        self.cap = cv2.VideoCapture(
            str(self.video_path)
        )

        if not self.cap.isOpened():

            raise RuntimeError(
                "Cannot open video."
            )

        self.fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )

        self.total_frames = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        self.width = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_WIDTH
            )
        )

        self.height = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_HEIGHT
            )
        )

        self.duration = (
            self.total_frames /
            self.fps
        )

        # one frame every second

        self.frame_step = int(
            round(self.fps)
        )

        self.records = []

        print("=" * 70)
        print("S4G-1.3")
        print("SYNCHRONIZED FRAME EXTRACTION")
        print("=" * 70)

        print(f"FPS            : {self.fps:.3f}")
        print(f"Frames         : {self.total_frames}")
        print(f"Duration       : {self.duration:.2f} s")
        print(f"Telemetry Rows : {len(self.telemetry)}")
        print()

    # --------------------------------------------------

    def nearest_telemetry(self, elapsed_ms):

        differences = np.abs(

            self.telemetry[
                "elapsed_ms"
            ].to_numpy()

            - elapsed_ms

        )

        idx = int(
            np.argmin(
                differences
            )
        )

        sync_error = float(
            differences[idx]
        )

        return idx, sync_error

    # --------------------------------------------------

    def extract_frames(self):

        print("=" * 70)
        print("EXTRACTING SYNCHRONIZED FRAMES")
        print("=" * 70)

        frame_index = 0
        saved_frames = 0

        while True:

            success, frame = self.cap.read()

            if not success:
                break

            if frame_index % self.frame_step == 0:

                elapsed_ms = (
                    frame_index /
                    self.fps
                ) * 1000.0

                telemetry_idx, sync_error = (
                    self.nearest_telemetry(
                        elapsed_ms
                    )
                )

                telemetry = self.telemetry.iloc[
                    telemetry_idx
                ]

                image_name = (
                    f"DJI_0995_t{int(elapsed_ms):09d}.jpg"
                )

                image_path = (
                    self.frame_dir /
                    image_name
                )

                cv2.imwrite(
                    str(image_path),
                    frame
                )

                self.records.append({

                    "sequence_id":
                        "DJI_0995",

                    "frame_id":
                        saved_frames + 1,

                    "image_name":
                        image_name,

                    "video_frame_idx":
                        frame_index,

                    "timestamp_ms":
                        round(elapsed_ms, 3),

                    "telemetry_index":
                        telemetry_idx,

                    "sync_error_ms":
                        round(sync_error, 3),

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

                })

                saved_frames += 1

                print(

                    f"{saved_frames:03d} | "

                    f"Frame {frame_index:5d} | "

                    f"{elapsed_ms:9.1f} ms | "

                    f"Sync {sync_error:6.2f} ms"

                )

            frame_index += 1

        self.cap.release()

        self.saved_frames = saved_frames

        print()
        print("=" * 70)
        print("FRAME EXTRACTION FINISHED")
        print("=" * 70)

        print(
            f"Frames Saved : {self.saved_frames}"
        )

        print(
            f"Output Folder : {self.frame_dir}"
        )

        print("=" * 70)

    # --------------------------------------------------

    def build_manifest(self):

        print()
        print("=" * 70)
        print("BUILDING FRAME MANIFEST")
        print("=" * 70)

        self.manifest = pd.DataFrame(
            self.records
        )

        self.manifest = self.manifest.sort_values(
            by="timestamp_ms"
        ).reset_index(drop=True)

        self.manifest.to_csv(

            self.manifest_path,

            index=False

        )

        print(
            f"Manifest Saved : {self.manifest_path.name}"
        )

        print(
            f"Manifest Rows  : {len(self.manifest)}"
        )

        print()

    # --------------------------------------------------

    def validate(self):

        print("=" * 70)
        print("VALIDATION")
        print("=" * 70)

        if len(self.manifest) != self.saved_frames:

            raise RuntimeError(

                "Mismatch between extracted frames "
                "and manifest rows."

            )

        if self.manifest["timestamp_ms"].is_monotonic_increasing:

            print("✓ Timestamp order OK")

        else:

            raise RuntimeError(
                "Timestamps are not increasing."
            )

        duplicate_names = self.manifest[
            "image_name"
        ].duplicated().sum()

        print(
            f"Duplicate Names : {duplicate_names}"
        )

        if duplicate_names != 0:

            raise RuntimeError(
                "Duplicate filenames detected."
            )

        missing = 0

        for image_name in self.manifest[
            "image_name"
        ]:

            image_path = (
                self.frame_dir /
                image_name
            )

            if not image_path.exists():

                missing += 1

        print(
            f"Missing Images  : {missing}"
        )

        if missing != 0:

            raise RuntimeError(
                "Manifest references missing images."
            )

        print()

        print(
            f"Mean Sync Error : "
            f"{self.manifest['sync_error_ms'].mean():.2f} ms"
        )

        print(
            f"Max Sync Error  : "
            f"{self.manifest['sync_error_ms'].max():.2f} ms"
        )

        print()

        print("✓ Manifest validation passed")

    # --------------------------------------------------

    def summary(self):

        print()
        print("=" * 70)
        print("S4G-1.3 SUMMARY")
        print("=" * 70)

        print(f"Video               : {self.video_path.name}")
        print(f"Telemetry           : {self.telemetry_path.name}")

        print()

        print(f"Video FPS           : {self.fps:.3f}")
        print(f"Video Frames        : {self.total_frames}")
        print(f"Video Duration      : {self.duration:.2f} s")

        print()

        print(f"Frames Extracted    : {self.saved_frames}")

        print(f"Frame Folder        :")
        print(f"  {self.frame_dir}")

        print()

        print(f"Manifest            :")
        print(f"  {self.manifest_path}")

        print()

        print(
            f"Average Sync Error  : "
            f"{self.manifest['sync_error_ms'].mean():.3f} ms"
        )

        print(
            f"Maximum Sync Error  : "
            f"{self.manifest['sync_error_ms'].max():.3f} ms"
        )

        print()

        print("✓ S4G-1.3 COMPLETED")

        print("=" * 70)

    # --------------------------------------------------

    def run(self):

        self.extract_frames()

        self.build_manifest()

        self.validate()

        self.summary()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    extractor = SyncedFrameExtractor()

    extractor.run()