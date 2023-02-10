import json                                 # import the json module
import itertools                           # import the itertools module
from PIL import Image, ImageDraw          # import Image and ImageDraw classes from the PIL module
import sys                                 # import the sys module

scaling_factor = float(sys.argv[1])       # take the scaling factor from the first argument passed to the script

print (scaling_factor)                    # print the scaling factor

def rasterize_geojson(geojson_file, output_dir):   # function to convert GeoJSON data to PNG images, one for each biome
    with open(geojson_file, "r") as f:             # open the input GeoJSON file for reading
        data = json.load(f)                        # load the GeoJSON data into a Python object
    polygs = data["features"]                     # extract the polygon features from the GeoJSON data
    img_width, img_height = 8192, 4096            # define the width and height of the image
    all_biomes = set([poly["properties"]["biome"] for poly in polygs])
                                                   # create a set of all the different biomes in the data
    for biome in all_biomes:                       # loop through the different biomes
        img = Image.new("L", (img_width, img_height), 0)   # create a new grayscale image of the specified size
        draw = ImageDraw.Draw(img)                 # create a draw object to draw on the image
        for poly in polygs:                         # loop through the polygon features
            if poly["properties"]["biome"] == biome:  # if the feature has the current biome
                for coords in poly["geometry"]["coordinates"]:   # loop through the coordinates of the polygon
                    coords = [ [ (coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2) ] for coord in coords ]
                                                    # scale and shift the coordinates to the center of the image
                    draw.polygon(list(itertools.chain(*coords)), fill=255)
                                                    # draw the polygon on the image using the fill value 255
        img = img.transpose(Image.FLIP_TOP_BOTTOM)  # flip the image along the vertical axis
        img.save(f"{output_dir}/biome_{biome}.png", "PNG")   # save the image as a PNG file with the biome name in the file name

rasterize_geojson("output.geojson", "terrain/")   # call the rasterize_geojson function
