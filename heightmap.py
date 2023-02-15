import json
import itertools
from PIL import Image, ImageDraw
import sys
import numpy as np

scaling_factor = float(sys.argv[1])


print (scaling_factor)

def rasterize_geojson(geojson_file, output_file):
    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]
    img_width, img_height = 8192, 4096
    img = Image.new("I;16", (img_width, img_height))
    draw = ImageDraw.Draw(img)

    heights = [poly["properties"]["height"] for poly in polygs]
    min_height = min(heights)
    max_height = max(heights)

    for poly in polygs:
        height = poly["properties"]["height"]
        if height < 0:
            color = 0
        else:
            normalized_height = (height - min_height) * 255 / (max_height - min_height)
            color = int(normalized_height)
        for coords in poly["geometry"]["coordinates"]:
            coords = [[(coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2)] for coord in coords]
            draw.polygon(list(itertools.chain(*coords)), fill=color)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")


rasterize_geojson("output.geojson", "map_data/heightmap.png")
