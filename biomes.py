import json
import itertools
from PIL import Image, ImageDraw
import sys
import os

scaling_factor = float(sys.argv[1])

print (scaling_factor)


def rasterize_geojson(geojson_file, output_dir):
    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]
    img_width, img_height = 8192, 4096
    all_biomes = set([poly["properties"]["biome"] for poly in polygs])

    for biome in all_biomes:
        img = Image.new("L", (img_width, img_height), 0)
        draw = ImageDraw.Draw(img)

        for poly in polygs:
            if poly["properties"]["biome"] == biome:
                for coords in poly["geometry"]["coordinates"]:
                    coords = [[(coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2)] for coord in coords]
                    draw.polygon(list(itertools.chain(*coords)), fill=255)

        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        img.save(f"{output_dir}/biome_{biome}.png", "PNG")

output_path = "gfx/map/terrain/"
output_folder = os.path.dirname(output_path)

if not os.path.exists(output_folder):
    os.makedirs(output_folder)


rasterize_geojson("output.geojson", output_path)


