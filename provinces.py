import json                                 # import the json module
import itertools                           # import the itertools module
from PIL import Image, ImageDraw          # import Image and ImageDraw classes from the PIL module
import sys                                 # import the sys module

scaling_factor = float(sys.argv[1])       # take the scaling factor from the first argument passed to the script

print (scaling_factor)                    # print the scaling factor

def hex_to_rgb(hex_color):                # function to convert a hexadecimal color string to an RGB tuple
    hex_color = hex_color.lstrip("#")     # remove the '#' symbol from the string
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rasterize_geojson(geojson_file, output_file):    # function to convert GeoJSON data to a PNG image
    with open(geojson_file, "r") as f:                # open the input GeoJSON file for reading
        data = json.load(f)                           # load the GeoJSON data into a Python object

    polygs = data["features"]                        # extract the polygon features from the GeoJSON data
    img_width, img_height = 8192, 4096               # define the width and height of the image
    img = Image.new("RGBA", (img_width, img_height)) # create a new RGBA image of the specified size
    draw = ImageDraw.Draw(img)                       # create a draw object to draw on the image
    for poly in polygs:                               # loop through the polyggon features
        color = hex_to_rgb(poly["properties"]["color"])   # convert the color string to an RGB tuple
        for coords in poly["geometry"]["coordinates"]:   # loop through the coordinates of the polygon
            coords = [ [ (coord[0] * scaling_factor) + (img_width / 2), (coord[1] * scaling_factor) + (img_height / 2) ] for coord in coords ]
                                                    # scale and shift the coordinates to the center of the image
            draw.polygon(list(itertools.chain(*coords)), fill=color + (255,))
                                                    # draw the polygon on the image using the converted color
    img = img.transpose(Image.FLIP_TOP_BOTTOM)       # flip the image along the vertical axis
    img.save(output_file, "PNG")                     # save the image as a PNG file

rasterize_geojson("output.geojson", "map_data/provinces.png")    # call the rasterize_geojson function
