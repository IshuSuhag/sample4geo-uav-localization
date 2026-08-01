import json
import os


class CoordinateConverter:

    def __init__(self, metadata_path):

        with open(metadata_path, "r") as f:
            metadata = json.load(f)

        world = metadata["world_file"]

        self.A = world["A"]
        self.B = world["B"]
        self.C = world["C"]

        self.D = world["D"]
        self.E = world["E"]
        self.F = world["F"]

    def pixel_to_world(self, u, v):
        """
        Convert image pixel -> world coordinate
        """

        X = self.A * u + self.B * v + self.C
        Y = self.D * u + self.E * v + self.F

        return X, Y

    def world_to_pixel(self, X, Y):
        """
        Convert world coordinate -> image pixel
        """

        u = (X - self.C) / self.A
        v = (Y - self.F) / self.E

        return u, v