from pathlib import Path
import cv2


class SmokeTestExtractor:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.video_path = (
            self.project_root /
            "datasets" /
            "raw" /
            "DJI_0995.MP4"
        )

        self.output_dir = (
            self.project_root /
            "datasets" /
            "smoke_test_frames"
        )

        self.output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.cap = cv2.VideoCapture(
            str(self.video_path)
        )

        if not self.cap.isOpened():

            raise RuntimeError(
                "Cannot open video."
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

        self.fps = self.cap.get(
            cv2.CAP_PROP_FPS
        )

    # --------------------------------------------------

    def extract(self):

        print("=" * 70)
        print("10 FRAME SMOKE TEST")
        print("=" * 70)

        frame_id = 1

        while frame_id <= 10:

            success, frame = self.cap.read()

            if not success:
                break

            filename = (
                self.output_dir /
                f"frame_{frame_id:06d}.jpg"
            )

            cv2.imwrite(
                str(filename),
                frame
            )

            print(
                f"Saved {filename.name}"
            )

            frame_id += 1

        self.cap.release()

        self.saved = frame_id - 1

    # --------------------------------------------------

    def verify(self):

        print()
        print("=" * 70)
        print("VERIFICATION")
        print("=" * 70)

        images = sorted(
            self.output_dir.glob("*.jpg")
        )

        print(
            f"Frames Saved : {len(images)}"
        )

        if len(images) != self.saved:

            raise RuntimeError(
                "Smoke test verification failed."
            )

        sample = cv2.imread(
            str(images[0])
        )

        h, w = sample.shape[:2]

        print(f"Resolution : {w} x {h}")

        print(f"First Frame : {images[0].name}")

        print(f"Last Frame  : {images[-1].name}")

        print()

        print("✓ Smoke Test Passed")

    # --------------------------------------------------

    def summary(self):

        print()
        print("=" * 70)
        print("SMOKE TEST COMPLETED")
        print("=" * 70)

        print(f"Video FPS        : {self.fps:.3f}")
        print(f"Video Resolution : {self.width} x {self.height}")
        print(f"Frames Tested    : {self.saved}")

        print(f"Output Folder    : {self.output_dir}")

        print("=" * 70)

    # --------------------------------------------------

    def run(self):

        self.extract()

        self.verify()

        self.summary()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    tester = SmokeTestExtractor()

    tester.run()