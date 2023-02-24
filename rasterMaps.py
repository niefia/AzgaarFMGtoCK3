import json
import itertools
from PIL import Image, ImageDraw
import numpy as np
import hextorgb
import os

scaling_factor = 50

def heightmap(geojson_file, output_file, scaling_factor):
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

def provincesCells(input_file, output_file, scaling_factor):
    with open(input_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]
    img_width, img_height = 8192, 4096
    img = Image.new("RGB", (img_width, img_height))
    draw = ImageDraw.Draw(img)
    for poly in polygs:
        color = hextorgb.hex_to_rgb(poly["properties"]["color"])
        for coords in poly["geometry"]["coordinates"]:
            coords = [ [ (coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2) ] for coord in coords ]
            draw.polygon(list(itertools.chain(*coords)), fill=color + (255,))
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    if not os.path.exists(os.path.dirname(output_file)):
        os.makedirs(os.path.dirname(output_file))
    img.save(output_file, "PNG")

def biomes(geojson_file, output_dir, scaling_factor):
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







#heightmap("output.geojson", "map_data/heightmap.png", scaling_factor)
#provincesCells("output.geojson", "map_data/provinces.png", scaling_factor)
#biomes("output.geojson", "gfx/map/terrain/", scaling_factor)