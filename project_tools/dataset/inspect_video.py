from pathlib import Path
import cv2
import re


class VideoInspector:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.raw_dir = (
            self.project_root /
            "datasets" /
            "raw"
        )

        self.video_path = (
            self.raw_dir /
            "DJI_0995.MP4"
        )

        self.srt_path = (
            self.raw_dir /
            "DJI_0995.SRT"
        )

        if not self.video_path.exists():
            raise FileNotFoundError(self.video_path)

        if not self.srt_path.exists():
            raise FileNotFoundError(self.srt_path)

        self.cap = cv2.VideoCapture(str(self.video_path))

        if not self.cap.isOpened():
            raise RuntimeError("Cannot open video.")

    # --------------------------------------------------

    def inspect_video(self):

        self.width = int(
            self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        self.height = int(
            self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        self.fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )

        self.total_frames = int(
            self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        self.duration = (
            self.total_frames /
            self.fps
        )

        fourcc = int(
            self.cap.get(cv2.CAP_PROP_FOURCC)
        )

        codec = "".join(
            chr((fourcc >> (8 * i)) & 0xFF)
            for i in range(4)
        )

        print("=" * 70)
        print("VIDEO INSPECTION")
        print("=" * 70)

        print(f"Codec         : {codec}")
        print(f"Width         : {self.width}")
        print(f"Height        : {self.height}")
        print(f"FPS           : {self.fps:.3f}")
        print(f"Frames        : {self.total_frames}")
        print(f"Duration (s)  : {self.duration:.3f}")

    # --------------------------------------------------

    def timestamp_to_ms(self, time_string):

        h, m, rest = time_string.split(":")

        s, ms = rest.split(",")

        return (
            int(h) * 3600000 +
            int(m) * 60000 +
            int(s) * 1000 +
            int(ms)
        )

    # --------------------------------------------------

    def inspect_srt(self):

        print()
        print("=" * 70)
        print("SRT INSPECTION")
        print("=" * 70)

        with open(
            self.srt_path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            lines = f.readlines()

        subtitle_lines = []

        for line in lines:

            if "-->" in line:

                subtitle_lines.append(
                    line.strip()
                )

        if len(subtitle_lines) == 0:

            raise RuntimeError(
                "Subtitle timing lines not found."
            )

        first = subtitle_lines[0]

        last = subtitle_lines[-1]

        start_time = first.split("-->")[0].strip()

        end_time = last.split("-->")[1].strip()

        start_ms = self.timestamp_to_ms(
            start_time
        )

        end_ms = self.timestamp_to_ms(
            end_time
        )

        self.srt_duration = (
            end_ms - start_ms
        ) / 1000

        print(
            f"SRT Duration (s) : {self.srt_duration:.3f}"
        )

    # --------------------------------------------------

    def compare(self):

        print()
        print("=" * 70)
        print("VIDEO vs SRT COMPARISON")
        print("=" * 70)

        difference = abs(
            self.duration -
            self.srt_duration
        )

        print(
            f"Video Duration : {self.duration:.3f} s"
        )

        print(
            f"SRT Duration   : {self.srt_duration:.3f} s"
        )

        print(
            f"Difference     : {difference:.3f} s"
        )

        print()

        if difference < 1.0:

            print("✓ Video and SRT are synchronized.")

        else:

            print("⚠ Duration mismatch detected.")
            print("Synchronization needs investigation.")

    # --------------------------------------------------

    def summary(self):

        print()
        print("=" * 70)
        print("VIDEO INSPECTION COMPLETED")
        print("=" * 70)

        print(f"Video File   : {self.video_path.name}")
        print(f"SRT File     : {self.srt_path.name}")
        print(f"Resolution   : {self.width} x {self.height}")
        print(f"FPS          : {self.fps:.3f}")
        print(f"Frames       : {self.total_frames}")

        self.cap.release()

    # --------------------------------------------------

    def run(self):

        self.inspect_video()

        self.inspect_srt()

        self.compare()

        self.summary()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    inspector = VideoInspector()

    inspector.run()