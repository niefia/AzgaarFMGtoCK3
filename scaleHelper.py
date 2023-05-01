import json
import pandas as pd


class ScaleInfo:
    # Class variables
    min_x = float('inf')
    max_x = float('-inf')
    min_y = float('inf')
    max_y = float('-inf')

    # Constructor
    def __init__(self, geojson_file, img_width=8192, img_height=4096):
        # Load the GeoJSON data from a file
        with open(geojson_file, "r") as f:
            data = json.load(f)

        # Initialize variables for minimum and maximum x and y values
        self.min_x = float('inf')
        self.max_x = float('-inf')
        self.min_y = float('inf')
        self.max_y = float('-inf')

        # Iterate through the features
        for feature in data["features"]:
            # Extract the coordinates
            coords = feature["geometry"]["coordinates"]

            # Iterate through each coordinate and update the minimum and maximum values if necessary
            for coord in coords:
                x, y = coord
                if x < self.min_x:
                    self.min_x = x
                if x > self.max_x:
                    self.max_x = x
                if y < self.min_y:
                    self.min_y = y
                if y > self.max_y:
                    self.max_y = y

            # Calculate the scaling factor to fit the polygons in the output image
            # It will scale with either height r width, whichever is larger
            self.scale_factor = max((self.max_x - self.min_x) / img_width, (self.max_y - self.min_y) / img_height)

            # Calculate the x and y offsets to center the polygons in the output image
            self.x_offset = (img_width - (self.max_x - self.min_x) / self.scale_factor) / 2
            self.y_offset = (img_height - (self.max_y - self.min_y) / self.scale_factor) / 2

    # Transform a coordinate to the output image
    def scale_coordinate(self, coord):
        "Note: This function does not account for the fact that images are flipped. This is bacsue there is other code"
        "that oe sthis later as part of their step and I don't feel like updateing that now."
        x, y = coord
        return (int((x - self.min_x) / self.scale_factor + self.x_offset),
                int((y - self.min_y) / self.scale_factor + self.y_offset))
