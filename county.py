import json
import itertools
from PIL import Image, ImageDraw
import sys
import colorsys

scaling_factor = 35

print (scaling_factor)

def generatecolor(province_number):
    if province_number == 0:
        return (0, 0, 0, 255)
    hue = province_number / 600
    saturation = 0.7
    value = 0.8
    rgb = colorsys.hsv_to_rgb(hue, saturation, value)
    return tuple(map(int, (rgb[0] * 255, rgb[1] * 255, rgb[2] * 255)))

def rasterize_geojson(geojson_file, output_file):
    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]
    img_width, img_height = 8192, 4096
    img = Image.new("RGBA", (img_width, img_height))
    draw = ImageDraw.Draw(img)
    for poly in polygs:
        province_number = poly["properties"]["province"]
        color = generatecolor(province_number)
        for coords in poly["geometry"]["coordinates"]:
            coords = [ [ (coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2) ] for coord in coords ]
            draw.polygon(list(itertools.chain(*coords)), fill=color)
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")

rasterize_geojson("output.geojson", "map_data/provincesmap.png")