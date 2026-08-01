from coordinate_utils import CoordinateConverter


converter = CoordinateConverter(
    "../../datasets/map_store/map_metadata.json"
)

test_points = [
    (0, 0),
    (635, 419),
    (1270, 838)
]

for u, v in test_points:

    X, Y = converter.pixel_to_world(u, v)

    u2, v2 = converter.world_to_pixel(X, Y)

    print("-" * 50)
    print(f"Original Pixel : ({u}, {v})")
    print(f"World Coord    : ({X:.4f}, {Y:.4f})")
    print(f"Recovered Pixel: ({u2:.6f}, {v2:.6f})")