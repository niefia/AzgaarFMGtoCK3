import json
import itertools
from PIL import Image, ImageDraw
import sys
import numpy as np

# Get the scaling factor from the command line argument
scaling_factor = float(sys.argv[1])

# Print the scaling factor
print (scaling_factor)

def rasterize_geojson(geojson_file, output_file):
    # Load the geojson data from the input file
    with open(geojson_file, "r") as f:
        data = json.load(f)

    # Get the list of polyggon features from the geojson data
    polygs = data["features"]
    # Set the width and height of the image
    img_width, img_height = 8192, 4096
    # Create a new image with mode "L" (8-bit pixels, black and white)
    img = Image.new("L", (img_width, img_height))
    # Create an ImageDraw object to draw on the image
    draw = ImageDraw.Draw(img)

    # Get the list of heights for each polygon
    heights = [poly["properties"]["height"] for poly in polygs]
    # Get the minimum and maximum heights
    min_height = min(heights)
    max_height = max(heights)

    # Loop through each polygon
    for poly in polygs:
        height = poly["properties"]["height"]
        # Assign a color based on the height
        if height < 0:
            color = 0
        else:
            # Normalize the height value to an 8-bit value (0-255)
            normalized_height = (height - min_height) * 255 / (max_height - min_height)
            color = int(normalized_height)
        # Loop through the coordinates of the polygon
        for coords in poly["geometry"]["coordinates"]:
            # Scale the coordinates by the scaling factor and center them on the image
            coords = [[(coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2)] for coord in coords]
            # Draw the polygon on the image with the assigned color
            draw.polygon(list(itertools.chain(*coords)), fill=color)
    # Flip the image vertically and save it as a PNG
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")

# Call the function with the input geojson file and output file
rasterize_geojson("output.geojson", "map_data/heightmap.png")
