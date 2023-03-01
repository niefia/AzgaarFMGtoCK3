import json
import itertools
from PIL import Image, ImageDraw
import numpy as np
import hextorgb
import os
import pandas as pd
import ast

# Declare global variables
scale_factor = None
min_x = None
max_x = None
min_y = None
max_y = None
x_offset = None
y_offset = None


def calculate_scaling_variables(geojson_file):
    global scale_factor, min_x, max_x, min_y, max_y, x_offset, y_offset, min_height, max_height

    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]

    # Determine the maximum and minimum values of x and y coordinates
    min_x = min(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_x = max(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    min_y = min(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_y = max(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)

    # Determine the width and height of the image
    img_width = 8192
    img_height = 4096

    # Calculate the scaling factor to fit the polygons in the output image
    scale_factor = max((max_x - min_x) / img_width, (max_y - min_y) / img_height)
    print("scalefactor:", scale_factor)

    # Calculate the x and y offsets to center the polygons in the output image
    x_offset = (img_width - (max_x - min_x) / scale_factor) / 2
    y_offset = (img_height - (max_y - min_y) / scale_factor) / 2





def heightmapAutoScaledfunc(geojson_file, output_file):
    global scale_factor, min_x, max_x, min_y, max_y, x_offset, y_offset

    # Calculate scaling variables if not already calculated
    if scale_factor is None:
        calculate_scaling_variables(geojson_file)

    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]

    img = Image.new("I;16", (8192, 4096))
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
            # Scale the coordinates based on the size of the image and center them
            coords = [[(coord[0] - min_x) / scale_factor + x_offset,
                       (coord[1] - min_y) / scale_factor + y_offset] for coord in coords]
            draw.polygon(list(itertools.chain(*coords)), fill=color)

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")

#heightmapAutoScaledfunc("output.geojson",  "heightmap.png")



def provinceMapBFSAutoScaled(file_path, output_folder):
    global scale_factor, min_x, max_x, min_y, max_y, x_offset, y_offset
    # read the Excel file
    df = pd.read_excel(file_path)

    # extract coordinates and colors
    coords_str = df['coordinates'].values
    colors_str = df['color'].values
    coords = []
    colors = []
    for coord_str, color_str in zip(coords_str, colors_str):
        coord_list = ast.literal_eval(coord_str)
        coord_list = [[float(x), float(y)] for x, y in coord_list[0]]
        coords.append(coord_list)
        colors.append(color_str)

    # Determine the width and height of the image
    img_width = 8192
    img_height = 4096

    # set up image
    img = Image.new('RGBA', (img_width, img_height), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # draw each polygon with scaling factor applied
    for coord, color in zip(coords, colors):

        # calculate the pixel value for each coordinate, with scaling factor applied and centered at the center_px
        coord_px = [(int((x - min_x) / scale_factor + x_offset),
                     int((y - min_y) / scale_factor + y_offset)) for x, y in coord]

        # draw polygon
        rgbcolor = hextorgb.bfs_hex_to_rgb(color)
        draw.polygon(coord_px, fill=rgbcolor, outline=None)

    # save image
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_folder)











#provinceMapBFSAutoScaled('BFSoutput.xlsx', 'provincesAS.png')





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

#AutoScaled Version of Heightmap
def heightmapAutoScaled(geojson_file, output_file):
    with open(geojson_file, "r") as f:
        data = json.load(f)

    polygs = data["features"]

    # Determine the maximum and minimum values of x and y coordinates
    min_x = min(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_x = max(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    min_y = min(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_y = max(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)

    # Determine the width and height of the image
    img_width = 8192
    img_height = 4096

    # Calculate the scaling factor to fit the polygons in the output image
    scale_factor = max((max_x - min_x) / img_width, (max_y - min_y) / img_height)
    print("scalefactor:", scale_factor)

    # Calculate the x and y offsets to center the polygons in the output image
    x_offset = (img_width - (max_x - min_x) / scale_factor) / 2
    y_offset = (img_height - (max_y - min_y) / scale_factor) / 2

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
            # Scale the coordinates based on the size of the image and center them
            coords = [[(coord[0] - min_x) / scale_factor + x_offset,
                       (coord[1] - min_y) / scale_factor + y_offset] for coord in coords]
            draw.polygon(list(itertools.chain(*coords)), fill=color)

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")


#heightmapAutoScaled("output.geojson",  "heightmap.png")





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

def biomesAutoScaled(geojson_file, output_dir):
    # Load the GeoJSON file
    with open(geojson_file, "r") as f:
        data = json.load(f)

    # Extract the polygons from the GeoJSON file
    polygs = data["features"]

    # Define the dimensions of the output image
    img_width, img_height = 8192, 4096

    # Determine the maximum and minimum values of x and y coordinates
    min_x = min(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_x = max(coord[0] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    min_y = min(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)
    max_y = max(coord[1] for poly in polygs for coords in poly["geometry"]["coordinates"] for coord in coords)

    # Calculate the scaling factor to fit the polygons in the output image
    scale_factor = max((max_x - min_x) / img_width, (max_y - min_y) / img_height)

    # Calculate the x and y offsets to center the polygons in the output image
    x_offset = (img_width - (max_x - min_x) / scale_factor) / 2
    y_offset = (img_height - (max_y - min_y) / scale_factor) / 2

    # Loop over all biomes in the data and create a separate image for each biome
    all_biomes = set([poly["properties"]["biome"] for poly in polygs])
    for biome in all_biomes:
        # Create a new image for this biome
        img = Image.new("L", (img_width, img_height), 0)
        draw = ImageDraw.Draw(img)

        # Loop over all polygons in the data and draw the ones that belong to this biome
        for poly in polygs:
            if poly["properties"]["biome"] == biome:
                for coords in poly["geometry"]["coordinates"]:
                    # Scale the coordinates based on the size of the image and center them
                    coords = [[(coord[0] - min_x) / scale_factor + x_offset,
                               (coord[1] - min_y) / scale_factor + y_offset] for coord in coords]
                    # Draw the polygon on the image
                    draw.polygon(list(itertools.chain(*coords)), fill=255)

        img = img.transpose(Image.FLIP_TOP_BOTTOM)
        # Save the biome image with the same filename as the heightmap image
        img.save(f"{output_dir}/biome_{biome}.png", "PNG")



#biomesAutoScaled("output.geojson",  "biomes")


#heightmap("output.geojson", "map_data/heightmap.png", scaling_factor)
#provincesCells("output.geojson", "map_data/provinces.png", scaling_factor)
#biomes("output.geojson", "gfx/map/terrain/", scaling_factor)