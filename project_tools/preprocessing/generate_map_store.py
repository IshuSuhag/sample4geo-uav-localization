import os
import json
import csv
import hashlib
from pathlib import Path

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont


class MapStoreGenerator:

    def __init__(self):

        self.project_root = Path(__file__).resolve().parents[2]

        self.raw_dir = self.project_root / "datasets" / "raw"

        self.map_store_dir = self.project_root / "datasets" / "map_store"

        self.tiles_dir = self.map_store_dir / "tiles"

        self.tiles_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.map_path = self.raw_dir / "satellite_map.png"

        self.metadata_path = (
            self.map_store_dir /
            "map_metadata.json"
        )

        self.manifest_path = (
            self.map_store_dir /
            "tile_manifest.csv"
        )

        self.grid_path = (
            self.map_store_dir /
            "tile_grid.png"
        )

        self.coverage_path = (
            self.map_store_dir /
            "coverage_map.png"
        )

        self.validation_path = (
            self.map_store_dir /
            "map_store_validation.json"
        )

        self.load_metadata()

        self.load_map()

        self.compute_hashes()

    # ----------------------------------------

    def load_metadata(self):

        with open(
            self.metadata_path,
            "r"
        ) as f:

            self.metadata = json.load(f)

        self.tile_size = self.metadata["tile_size_px"]

        self.stride = self.metadata["stride_px"]

        world = self.metadata["world_file"]

        self.A = world["A"]
        self.B = world["B"]
        self.C = world["C"]

        self.D = world["D"]
        self.E = world["E"]
        self.F = world["F"]

    # ----------------------------------------

    def load_map(self):

        self.image = Image.open(
            self.map_path
        ).convert("RGB")

        self.width, self.height = self.image.size

        print()

        print("=" * 70)

        print("Sample4Geo Map Store Generator")

        print("=" * 70)

        print(f"Width  : {self.width}")

        print(f"Height : {self.height}")

        print(f"Tile   : {self.tile_size}")

        print(f"Stride : {self.stride}")

        print("=" * 70)

    # ----------------------------------------

    def compute_hashes(self):

        with open(
            self.map_path,
            "rb"
        ) as f:

            self.map_checksum = hashlib.sha256(
                f.read()
            ).hexdigest()

        config = json.dumps(
            self.metadata,
            sort_keys=True
        )

        self.config_hash = hashlib.sha256(
            config.encode()
        ).hexdigest()

    # ----------------------------------------

    def pixel_to_world(
        self,
        u,
        v
    ):

        X = self.A * u + self.B * v + self.C

        Y = self.D * u + self.E * v + self.F

        return X, Y

    # ----------------------------------------

    def generate_positions(
        self,
        length
    ):

        positions = list(
            range(
                0,
                length - self.tile_size + 1,
                self.stride
            )
        )

        final_position = (
            length -
            self.tile_size
        )

        if positions[-1] != final_position:

            positions.append(
                final_position
            )

        return positions

    # ----------------------------------------

    def prepare(self):

        self.x_positions = self.generate_positions(
            self.width
        )

        self.y_positions = self.generate_positions(
            self.height
        )

        self.coverage = Image.new(
            "I",
            (
                self.width,
                self.height
            ),
            0
        )

        self.coverage_pixels = (
            self.coverage.load()
        )

        self.grid_image = (
            self.image.copy()
        )

        self.draw = ImageDraw.Draw(
            self.grid_image
        )

        self.rows = []

        self.total_tiles = 0

        print()

        print("Preparing Tile Generation...")

        print()

        print(
            f"Columns : {len(self.x_positions)}"
        )

        print(
            f"Rows    : {len(self.y_positions)}"
        )

        print(
            f"Tiles   : {len(self.x_positions)*len(self.y_positions)}"
        )

    # ----------------------------------------

    def generate_tiles(self):

        print()

        print("=" * 70)
        print("Generating Tiles...")
        print("=" * 70)

        try:
            font = ImageFont.load_default()
        except:
            font = None

        for row_idx, top in enumerate(self.y_positions):

            for col_idx, left in enumerate(self.x_positions):

                right = left + self.tile_size
                bottom = top + self.tile_size

                tile = self.image.crop(
                    (
                        left,
                        top,
                        right,
                        bottom
                    )
                )

                tile_id = (
                    f"R{row_idx:02d}"
                    f"C{col_idx:02d}"
                )

                filename = (
                    f"tile_r{row_idx:02d}"
                    f"_c{col_idx:02d}.png"
                )

                tile.save(
                    self.tiles_dir /
                    filename
                )

                center_u = (
                    left +
                    self.tile_size / 2
                )

                center_v = (
                    top +
                    self.tile_size / 2
                )

                min_x, max_y = self.pixel_to_world(
                    left,
                    top
                )

                max_x, min_y = self.pixel_to_world(
                    right,
                    bottom
                )

                self.rows.append(

                    {
                        "map_id":
                            self.metadata["map_id"],

                        "tile_id":
                            tile_id,

                        "filename":
                            filename,

                        "row_idx":
                            row_idx,

                        "col_idx":
                            col_idx,

                        "left_px":
                            left,

                        "top_px":
                            top,

                        "right_px":
                            right,

                        "bottom_px":
                            bottom,

                        "center_u_px":
                            center_u,

                        "center_v_px":
                            center_v,

                        "min_x":
                            min_x,

                        "max_x":
                            max_x,

                        "min_y":
                            min_y,

                        "max_y":
                            max_y,

                        "tile_size_px":
                            self.tile_size,

                        "stride_px":
                            self.stride,

                        "map_checksum":
                            self.map_checksum,

                        "config_hash":
                            self.config_hash

                    }

                )

                self.draw.rectangle(

                    [
                        (left, top),
                        (right, bottom)
                    ],

                    outline="red",
                    width=2

                )

                if font is not None:

                    self.draw.text(

                        (
                            left + 4,
                            top + 4
                        ),

                        tile_id,

                        fill="yellow",

                        font=font

                    )

                for y in range(top, bottom):

                    if y >= self.height:
                        continue

                    for x in range(left, right):

                        if x >= self.width:
                            continue

                        self.coverage_pixels[
                            x,
                            y
                        ] += 1

                self.total_tiles += 1

        print()

        print(
            f"Generated {self.total_tiles} tiles."
        )

    # ----------------------------------------

    def save_manifest(self):

        print()

        print("=" * 70)
        print("Saving Manifest...")
        print("=" * 70)

        columns = [

            "map_id",

            "tile_id",

            "filename",

            "row_idx",

            "col_idx",

            "left_px",

            "top_px",

            "right_px",

            "bottom_px",

            "center_u_px",

            "center_v_px",

            "min_x",

            "max_x",

            "min_y",

            "max_y",

            "tile_size_px",

            "stride_px",

            "map_checksum",

            "config_hash"

        ]

        with open(

            self.manifest_path,

            "w",

            newline=""

        ) as csvfile:

            writer = csv.DictWriter(

                csvfile,

                fieldnames=columns

            )

            writer.writeheader()

            writer.writerows(

                self.rows

            )

        print("Manifest Saved.")

        print(
            self.manifest_path
        )

    # ----------------------------------------

    def save_visualizations(self):

        print()

        print("=" * 70)
        print("Saving Visualizations...")
        print("=" * 70)

        self.grid_image.save(
            self.grid_path
        )

        max_value = 0

        for y in range(self.height):

            for x in range(self.width):

                if self.coverage_pixels[x, y] > max_value:
                    max_value = self.coverage_pixels[x, y]

        coverage_img = Image.new(
            "RGB",
            (
                self.width,
                self.height
            )
        )

        coverage_draw = coverage_img.load()

        for y in range(self.height):

            for x in range(self.width):

                value = self.coverage_pixels[x, y]

                if max_value == 0:
                    intensity = 0
                else:
                    intensity = int(
                        255 * value / max_value
                    )

                coverage_draw[x, y] = (
                    intensity,
                    0,
                    255 - intensity
                )

        coverage_img.save(
            self.coverage_path
        )

        print("Tile Grid Saved")

        print("Coverage Map Saved")

    # ----------------------------------------

    def validate(self):

        print()

        print("=" * 70)
        print("Running Validation...")
        print("=" * 70)

        zero_pixels = 0

        minimum = 999999

        maximum = 0

        for y in range(self.height):

            for x in range(self.width):

                value = self.coverage_pixels[x, y]

                if value == 0:
                    zero_pixels += 1

                if value < minimum:
                    minimum = value

                if value > maximum:
                    maximum = value

        validation = {

            "map_id":
                self.metadata["map_id"],

            "map_width":
                self.width,

            "map_height":
                self.height,

            "tile_size":
                self.tile_size,

            "stride":
                self.stride,

            "rows":
                len(self.y_positions),

            "columns":
                len(self.x_positions),

            "tiles_generated":
                self.total_tiles,

            "coverage": {

                "minimum":
                    minimum,

                "maximum":
                    maximum,

                "zero_pixels":
                    zero_pixels,

                "complete":
                    zero_pixels == 0

            },

            "checksums": {

                "map_checksum":
                    self.map_checksum,

                "config_hash":
                    self.config_hash

            }

        }

        with open(

            self.validation_path,

            "w"

        ) as f:

            json.dump(

                validation,

                f,

                indent=4

            )

        print("Validation Saved")

        print()

        print(
            f"Minimum Coverage : {minimum}"
        )

        print(
            f"Maximum Coverage : {maximum}"
        )

        print(
            f"Zero Coverage Pixels : {zero_pixels}"
        )

        if zero_pixels == 0:

            print()

            print("✓ COMPLETE MAP COVERAGE VERIFIED")

        else:

            print()

            print("✗ COVERAGE FAILED")

    # ----------------------------------------

    def run(self):

        self.prepare()

        self.generate_tiles()

        self.save_manifest()

        self.save_visualizations()

        self.validate()

        print()
        print("=" * 70)
        print("MAP STORE GENERATION COMPLETED")
        print("=" * 70)

        print(f"Map Width      : {self.width}")
        print(f"Map Height     : {self.height}")
        print(f"Tile Size      : {self.tile_size}")
        print(f"Stride         : {self.stride}")
        print(f"Rows           : {len(self.y_positions)}")
        print(f"Columns        : {len(self.x_positions)}")
        print(f"Total Tiles    : {self.total_tiles}")

        print()
        print("Generated Files")
        print("-----------------------------")
        print(f"Tiles Folder            : {self.tiles_dir}")
        print(f"Tile Manifest           : {self.manifest_path}")
        print(f"Tile Grid               : {self.grid_path}")
        print(f"Coverage Map            : {self.coverage_path}")
        print(f"Validation JSON         : {self.validation_path}")

        print()
        print("Checksums")
        print("-----------------------------")
        print(f"Map SHA256  : {self.map_checksum}")
        print(f"Config Hash : {self.config_hash}")

        print()
        print("=" * 70)
        print("S4G-0R.3 FINISHED")
        print("=" * 70)


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    generator = MapStoreGenerator()

    generator.run()