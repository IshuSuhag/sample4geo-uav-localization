from pathlib import Path
import json
import numpy as np


class WorldTransformValidator:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        metadata_path = (
            self.project_root /
            "datasets" /
            "map_store" /
            "map_metadata.json"
        )

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        wf = metadata["world_file"]

        self.A = wf["A"]
        self.B = wf["B"]
        self.C = wf["C"]
        self.D = wf["D"]
        self.E = wf["E"]
        self.F = wf["F"]

        self.width = metadata["width_px"]
        self.height = metadata["height_px"]

        self.M = np.array([
            [self.A, self.B],
            [self.D, self.E]
        ])

        self.M_inv = np.linalg.inv(self.M)

    # --------------------------------------------------

    def pixel_to_world(self, x, y):

        wx = (
            self.A * x +
            self.B * y +
            self.C
        )

        wy = (
            self.D * x +
            self.E * y +
            self.F
        )

        return wx, wy

    # --------------------------------------------------

    def world_to_pixel(self, wx, wy):

        vec = np.array([
            wx - self.C,
            wy - self.F
        ])

        px = self.M_inv @ vec

        return (
            float(px[0]),
            float(px[1])
        )

    # --------------------------------------------------

    def validate(self):

        print("=" * 70)
        print("WORLD TRANSFORM VALIDATION")
        print("=" * 70)

        test_points = [

            (0, 0),

            (
                self.width / 2,
                self.height / 2
            ),

            (
                self.width - 1,
                self.height - 1
            )

        ]

        max_error = 0.0

        for idx, (px, py) in enumerate(test_points, start=1):

            wx, wy = self.pixel_to_world(
                px,
                py
            )

            px2, py2 = self.world_to_pixel(
                wx,
                wy
            )

            error = np.sqrt(

                (px - px2) ** 2 +

                (py - py2) ** 2

            )

            max_error = max(
                max_error,
                error
            )

            print(f"\nTest Point {idx}")

            print(f"Pixel  : ({px:.6f}, {py:.6f})")

            print(f"World  : ({wx:.6f}, {wy:.6f})")

            print(f"Back   : ({px2:.6f}, {py2:.6f})")

            print(f"Error  : {error:.12f} px")

        print()

        print("=" * 70)

        print(
            f"Maximum Round-Trip Error : {max_error:.12e} px"
        )

        if max_error < 1e-6:

            print()

            print("✓ PASS")

            print(
                "Affine transform validated."
            )

        else:

            print()

            print("✗ FAIL")

            print(
                "Round-trip error exceeds tolerance."
            )

        print("=" * 70)

    # --------------------------------------------------

    def run(self):

        self.validate()


# ==========================================================
# Main
# ==========================================================

if __name__ == "__main__":

    validator = WorldTransformValidator()

    validator.run()