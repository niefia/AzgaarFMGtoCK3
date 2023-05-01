from pandas.io import json

class ScaleInfo:
    def __init__(self, geojson_file, img_width = 8192, img_height = 4096):
        with open(geojson_file, "r") as f:
            data = json.load(f)

        polygs = data["features"]

        # Determine the maximum and minimum values of x and y coordinates
        min_x = min(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
        max_x = max(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
        min_y = min(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
        max_y = max(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)


        # Calculate the scaling factor to fit the polygons in the output image
        self.scale_factor = max((max_x - min_x) / img_width, (max_y - min_y) / img_height)
        print("scalefactor:", self.scale_factor)

        # Calculate the x and y offsets to center the polygons in the output image
        self.x_offset = (img_width - (max_x - min_x) / self.scale_factor) / 2
        self.y_offset = (img_height - (max_y - min_y) / self.scale_factor) / 2
