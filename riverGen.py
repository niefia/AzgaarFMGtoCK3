import json
from PIL import Image, ImageDraw
import numpy as np
import sys

# set scaling factor
scaling_factor = float(sys.argv[1])

# print the scaling factor
print(scaling_factor)


def paint_land_sea(heightmap_file, output_file):
    """Takes in a heightmap file, paints land white and sea magenta, outputs a PIL image object."""

    img = Image.open(heightmap_file)
    img = img.convert('RGB')

    # converting to numpy array for faster processing
    color_array = np.array(img)
    red, green, blue = color_array.T  # Temporarily unpack the bands for readability

    # Replace sea with magenta, land with white
    sea_pixels = ((red == 0) & (blue == 0) & (green == 0)).T
    color_array[sea_pixels] = (255, 0, 128)  # replacing sea pixels
    color_array[~sea_pixels] = (255, 255, 255)  # replacing "not-sea" pixels

    img = Image.fromarray(color_array)
    img.save(output_file, "PNG")


def draw_rivers(landsea_image, rivers_geojson, output_file):
    """Implements the river-drawing algorithm, taking in a land-sea painted image and a river geojson file."""

    # load the painted land sea map
    img = Image.open(landsea_image)
    # Flip top to bottom for right coordinate alignment
    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    # get image width and height
    img_width, img_height = img.size
    # Create an ImageDraw object to draw on the image
    draw = ImageDraw.Draw(img)

    with open(rivers_geojson, "r") as f:
        data = json.load(f)

    # get rivers
    rivers = data["features"]

    for river in rivers:
        flat_coords = np.array([item * scaling_factor for sublist in river["geometry"]["coordinates"]
                                for item in sublist])
        centred_coords = flat_coords + np.tile([img_width / 2, img_height / 2], int(flat_coords.size / 2))
        centred_coords = centred_coords.reshape(int(len(centred_coords) / 2), 2)  # reshaping into 2-column array

        if river["properties"]["parent"] == 0 or river["properties"]["parent"] == river["properties"]["id"]:
            start_color = (0, 255, 0)  # beginning color is green for source river
        else:
            centred_coords = centred_coords[::-1]  # starting from the end of the river if the river ends in a parent
            start_color = (255, 0, 0)  # beginning color is red for tributary river

        draw_coords = np.floor(centred_coords[0]).reshape(1, 2)  # first coordinates to add

        for row in range(1, centred_coords[1:].shape[0]):
            new_coords = np.floor(centred_coords[row]).reshape(1, 2)
            if (np.abs(new_coords - draw_coords[-1]).sum(axis=1) >= 2)[0]:  # if both x and y coordinates jump
                jump_coord = np.argmin(np.abs(draw_coords[-1]-centred_coords[row]))  # the closest of x or y
                new_coords[0, jump_coord] = draw_coords[-1, jump_coord]
                draw_coords = np.append(draw_coords, new_coords, axis=0)
            elif (np.abs(new_coords - draw_coords[-1]).sum(axis=1) == 1)[0]:  # at least one of x or y moves
                draw_coords = np.append(draw_coords, new_coords, axis=0)

        draw.line(sum(draw_coords.tolist(), []), fill=(0, 0, 255))
        draw.point(draw_coords[0].tolist(), fill=start_color)  # just the starting point

    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")


paint_land_sea("map_data/heightmap.png", "map_data/landsea.png")
draw_rivers("map_data/landsea.png", "rivers.geojson", "map_data/rivermap.png")