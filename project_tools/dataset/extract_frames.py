from pathlib import Path
import cv2


class VideoFrameExtractor:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.raw_dir = (
            self.project_root /
            "datasets" /
            "raw"
        )

        self.frames_dir = (
            self.project_root /
            "datasets" /
            "frames"
        )

        self.frames_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.video_path = (
            self.raw_dir /
            "DJI_0995.MP4"
        )

        if not self.video_path.exists():

            raise FileNotFoundError(
                self.video_path
            )

        self.cap = cv2.VideoCapture(
            str(self.video_path)
        )

        if not self.cap.isOpened():

            raise RuntimeError(
                "Unable to open video."
            )

        self.total_frames = int(
            self.cap.get(
                cv2.CAP_PROP_FRAME_COUNT
            )
        )

        self.fps = self.cap.get(
            cv2.CAP_PROP_FPS
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

    # --------------------------------------------------

    def info(self):

        print("=" * 70)
        print("DJI VIDEO INSPECTION")
        print("=" * 70)

        print(f"Video : {self.video_path.name}")

        print(f"Frames : {self.total_frames}")

        print(f"FPS : {self.fps:.2f}")

        print(f"Resolution : {self.width} x {self.height}")

        print("=" * 70)

    # --------------------------------------------------

    def extract_frames(self):

        print()
        print("=" * 70)
        print("Extracting Frames")
        print("=" * 70)

        frame_number = 1

        while True:

            success, frame = self.cap.read()

            if not success:
                break

            filename = (
                f"frame_{frame_number:06d}.jpg"
            )

            output_path = (
                self.frames_dir /
                filename
            )

            cv2.imwrite(
                str(output_path),
                frame
            )

            if (
                frame_number == 1
                or frame_number % 500 == 0
                or frame_number == self.total_frames
            ):

                progress = (
                    frame_number /
                    self.total_frames
                ) * 100

                print(
                    f"Frame {frame_number:6d} / "
                    f"{self.total_frames:6d} "
                    f"({progress:.1f}%)"
                )

            frame_number += 1

        self.cap.release()

        self.extracted_frames = frame_number - 1

        print()

        print(
            f"Extracted {self.extracted_frames} frames."
        )

    # --------------------------------------------------

    def verify(self):

        print()
        print("=" * 70)
        print("Verification")
        print("=" * 70)

        images = sorted(
            self.frames_dir.glob("*.jpg")
        )

        print(
            f"Frames on Disk : {len(images)}"
        )

        if len(images) != self.extracted_frames:

            raise RuntimeError(
                "Frame count mismatch."
            )

        first = images[0].name
        last = images[-1].name

        print(f"First Frame : {first}")
        print(f"Last Frame  : {last}")

        sample = cv2.imread(
            str(images[0])
        )

        h, w = sample.shape[:2]

        print(
            f"Image Size : {w} x {h}"
        )

        print()

        print("✓ Verification Passed")

    # --------------------------------------------------

    def summary(self):

        print()
        print("=" * 70)
        print("FRAME EXTRACTION COMPLETED")
        print("=" * 70)

        print(f"Input Video      : {self.video_path}")
        print(f"Output Folder    : {self.frames_dir}")
        print(f"Frames Extracted : {self.extracted_frames}")
        print(f"Video FPS        : {self.fps:.2f}")
        print(f"Resolution       : {self.width} x {self.height}")

        duration = self.extracted_frames / self.fps

        print(f"Duration (sec)   : {duration:.2f}")

        print("=" * 70)

    # --------------------------------------------------

    def run(self):

        self.info()

        self.extract_frames()

        self.verify()

        self.summary()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    extractor = VideoFrameExtractor()

    extractor.run()