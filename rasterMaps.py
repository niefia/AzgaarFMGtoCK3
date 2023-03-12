import json
import itertools
from PIL import Image, ImageDraw
import numpy as np
import hextorgb
import os
import pandas as pd
import ast
from PIL import Image
import numpy as np

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




def paint_land_sea_mask(heightmap_file, output_file):
    """Takes in a heightmap file, paints land white and sea magenta, outputs a PIL image object."""

    img = Image.open(heightmap_file)
    img = img.convert('RGB')

    # converting to numpy array for faster processing
    color_array = np.array(img)
    red, green, blue = color_array.T  # Temporarily unpack the bands for readability

    # Replace sea with magenta, land with white
    sea_pixels = ((red == 0) & (blue == 0) & (green == 0)).T
    color_array[sea_pixels] = (0, 0, 0)  # replacing sea pixels
    color_array[~sea_pixels] = (255, 255, 255)  # replacing "not-sea" pixels

    img = Image.fromarray(color_array)
    img.save(output_file, "PNG")

paint_land_sea_mask("heightmap.png","masksea.png")




def create_masked_image(black_image_path, white_image_path, mask_image_path, output_image_path):
    # Load the black and white images
    black_image = np.array(Image.open(black_image_path))
    white_image = np.array(Image.open(white_image_path))

    # Load the mask image as a numpy array
    mask_image = np.array(Image.open(mask_image_path))

    # Create a new array for the output image
    output_image = np.zeros_like(mask_image, dtype=np.uint8)

    # Mask the black and white images using the mask
    black_masked = black_image.copy()
    black_masked[mask_image[:, :, 0] == 255] = 0
    black_masked = black_masked[:, :, :3]  # remove alpha channel
    white_masked = white_image.copy()
    white_masked[mask_image[:, :, 0] == 0] = 0
    white_masked = white_masked[:, :, :3]  # remove alpha channel

    # Add a brown border outline where the white and black of the mask image touch
    mask = mask_image[:, :, 0]
    mask_left = np.hstack([mask[:, 1:], np.zeros((mask.shape[0], 1), dtype=np.uint8)])
    mask_right = np.hstack([np.zeros((mask.shape[0], 1), dtype=np.uint8), mask[:, :-1]])
    mask_top = np.vstack([mask[1:, :], np.zeros((1, mask.shape[1]), dtype=np.uint8)])
    mask_bottom = np.vstack([np.zeros((1, mask.shape[1]), dtype=np.uint8), mask[:-1, :]])
    border_mask = (mask != mask_left) | (mask != mask_right) | (mask != mask_top) | (mask != mask_bottom)
    output_image[border_mask] = [150, 75, 0]

    # Combine the masked images to create the output image
    output_image = output_image + black_masked + white_masked

    # Save the output image
    Image.fromarray(output_image).save(output_image_path)


def produce_outline(mask_image_path, output_image_path):
    # Load the mask image as a numpy array
    mask_image = np.array(Image.open(mask_image_path))

    # Create a new array for the output image
    output_image = np.zeros_like(mask_image, dtype=np.uint8)

    # Add a brown border outline where the white and black of the mask image touch
    mask = mask_image[:, :, 0]
    mask_left = np.hstack([mask[:, 1:], np.zeros((mask.shape[0], 1), dtype=np.uint8)])
    mask_right = np.hstack([np.zeros((mask.shape[0], 1), dtype=np.uint8), mask[:, :-1]])
    mask_top = np.vstack([mask[1:, :], np.zeros((1, mask.shape[1]), dtype=np.uint8)])
    mask_bottom = np.vstack([np.zeros((1, mask.shape[1]), dtype=np.uint8), mask[:-1, :]])
    border_mask = (mask != mask_left) | (mask != mask_right) | (mask != mask_top) | (mask != mask_bottom)
    output_image[border_mask] = [77, 55, 41]

    # Save the output image
    Image.fromarray(output_image).save(output_image_path)


def overlay_png_on_dds(png_filename, dds_filename, output_filename):
    # Open the png image and extract its non-black pixels
    png_image = Image.open(png_filename)
    png_pixels = png_image.load()
    png_width, png_height = png_image.size
    non_black_pixels = []
    for y in range(png_height):
        for x in range(png_width):
            if png_pixels[x, y] != (0, 0, 0):
                non_black_pixels.append((x, y))

    # Open the dds image and create a new image to hold the overlay
    dds_image = Image.open(dds_filename)
    overlay_image = Image.new("RGBA", dds_image.size, (0, 0, 0, 0))

    # Place the non-black pixels on the overlay
    overlay_pixels = overlay_image.load()
    for pixel in non_black_pixels:
        overlay_pixels[pixel[0], pixel[1]] = png_pixels[pixel[0], pixel[1]] + (255,)

    # Combine the overlay with the dds image and save the result
    result_image = Image.alpha_composite(dds_image.convert("RGBA"), overlay_image)
    result_image.save(output_filename)


#create_masked_image('sea_image.png', 'land_image.png', 'masksea.png', 'flatmap1.dds')

#produce_outline('masksea.png','flatmapBorder.png')

#overlay_png_on_dds('flatmapBorder.png','flatmap1.dds','flatmap.dds')

#biomesAutoScaled("output.geojson",  "biomes")


#heightmap("output.geojson", "map_data/heightmap.png", scaling_factor)
#provincesCells("output.geojson", "map_data/provinces.png", scaling_factor)
#biomes("output.geojson", "gfx/map/terrain/", scaling_factor)