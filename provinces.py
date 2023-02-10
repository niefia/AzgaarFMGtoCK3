import json
import itertools
from PIL import Image, ImageDraw
import sys


scaling_factor = float(sys.argv[1])

print (scaling_factor)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rasterize_geojson(geojson_file, output_file):
    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]
    img_width, img_height = 8192, 4096
    img = Image.new("RGBA", (img_width, img_height))
    draw = ImageDraw.Draw(img)
    for poly in polygs:
        color = hex_to_rgb(poly["properties"]["color"])
        for coords in poly["geometry"]["coordinates"]:
            coords = [ [ (coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2) ] for coord in coords ]
            draw.polygon(list(itertools.chain(*coords)), fill=color + (255,))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")

rasterize_geojson("output.geojson", "map_data/provinces.png")