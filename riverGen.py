import json
from PIL import Image, ImageDraw
import numpy as np
import sys

# set scaling factor
scaling_factor = 30

# print the scaling factor
print("Scaling factor: " + str(scaling_factor))

#Constants for blue, greeen and magenta
#blue = (0, 0, 255)
#green = (0, 255, 0)
#magenta = (255, 0, 255)

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


def draw_mainstreams(landsea_image, rivers_geojson, output_file):
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
        if river["properties"]["parent"] == 0: #If the river is a mainstrem, then the parent will be 0
            flat_coords = np.array([item * scaling_factor for sublist in river["geometry"]["coordinates"]
                                    for item in sublist])
            centred_coords = flat_coords + np.tile([img_width / 2, img_height / 2], int(flat_coords.size / 2))
            centred_coords = centred_coords.reshape(int(len(centred_coords) / 2), 2)  # reshaping into 2-column array

            start_color = (0, 255, 0)  # beginning color is green for source river

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

# Checks for Specific error where Multiple Blue pixels are around Green Source, replaces with White automatically
def correct_rivermap(image_path, output_file):
    # Load the image
    with Image.open(image_path) as image:
        # Get the pixel data
        pixels = image.load()
        # Create a new image to write to
        new_image = Image.new(image.mode, image.size, color=(255, 255, 255))
        new_pixels = new_image.load()
        # Loop through the pixels
        for y in range(image.size[1]):
            for x in range(image.size[0]):
                # Check if the pixel is green
                if pixels[x, y] == (0, 255, 0):
                    # Count the adjacent blue pixels
                    count = 0
                    adj_blues = []
                    if x > 0 and pixels[x-1, y] == (0, 0, 255):
                        count += 1
                        adj_blues.append((x-1, y))
                    if x < image.size[0]-1 and pixels[x+1, y] == (0, 0, 255):
                        count += 1
                        adj_blues.append((x+1, y))
                    if y > 0 and pixels[x, y-1] == (0, 0, 255):
                        count += 1
                        adj_blues.append((x, y-1))
                    if y < image.size[1]-1 and pixels[x, y+1] == (0, 0, 255):
                        count += 1
                        adj_blues.append((x, y+1))
                    # Check if the green pixel has more than one adjacent blue pixel
                    if count > 1:
                        for bx, by in adj_blues:
                            # Check if the blue pixel has only one adjacent blue pixel
                            bcount = 0
                            if bx > 0 and pixels[bx-1, by] == (0, 0, 255):
                                bcount += 1
                            if bx < image.size[0]-1 and pixels[bx+1, by] == (0, 0, 255):
                                bcount += 1
                            if by > 0 and pixels[bx, by-1] == (0, 0, 255):
                                bcount += 1
                            if by < image.size[1]-1 and pixels[bx, by+1] == (0, 0, 255):
                                bcount += 1
                            if bcount == 0:
                                # Replace the blue pixel with white
                                new_pixels[bx, by] = (255, 255, 255)
                                break
                        else:
                            print("Error at ({}, {})".format(x, y))
                            # Copy the pixel from the original image
                            new_pixels[x, y] = pixels[x, y]
                    else:
                        # Copy the pixel from the original image
                        new_pixels[x, y] = pixels[x, y]
                else:
                    # Copy the pixel from the original image
                    new_pixels[x, y] = pixels[x, y]
        # Save the new image
        new_image.save(output_file)

#Use Landsea file as mask image as most Blue errors happen in sea, so can be masked anyway
def mask_landsea(image_path, mask_path, output_image_path):
    # Load the original image
    img = Image.open(image_path)

    # Load the mask image
    mask = Image.open(mask_path)

    # Convert the mask image to RGB
    mask = mask.convert('RGB')

    # Get the size of the mask
    width, height = mask.size

    # Iterate over all pixels in the mask image
    for x in range(width):
        print (x,"/8192")
        for y in range(height):
            # Get the color of the pixel
            r, g, b = mask.getpixel((x, y))
            # If the color is magenta (FF0080), set the corresponding pixel in the original image to transparent
            if (r == 255) and (g == 0) and (b == 128):
                img.putpixel((x, y), (255, 0, 128, 0))

    # Save the modified image
    img.save(output_image_path)

#Checks for error of more than 2 touching Blue pixels, Does not correct yet
def check_image_for_more_than_two_blue(image_path):
    # Load the image
    image = Image.open(image_path)
    # Get the pixel data
    pixels = image.load()
    bpc = 0
    # Loop through the pixels
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            # Check if the pixel is green
            if pixels[x, y] == (0, 0, 255):
                # Count the adjacent blue pixels
                count = 0
                if x > 0 and pixels[x-1, y] == (0, 0, 255):
                    count += 1
                if x < image.size[0]-1 and pixels[x+1, y] == (0, 0, 255):
                    count += 1
                if y > 0 and pixels[x, y-1] == (0, 0, 255):
                    count += 1
                if y < image.size[1]-1 and pixels[x, y+1] == (0, 0, 255):
                    count += 1
                # Check if the green pixel has more than one adjacent blue pixel
                if count > 2:
                    print("Error Blue pixel with more than 2 adjacent at ({}, {})".format(x, y), "Blue Pixel Error:",(bpc))
                    bpc += 1



# Test Region of the code

#Path to folder containing heightmap.png, landsea.png, rivers.geojson when testing
path = "River_Test/"

paint_land_sea(path + "heightmap.png", path + "landsea.png")
draw_mainstreams(path + "landsea.png", path + "rivers.geojson", path + "rivermap_mainstreams.png")
correct_rivermap(path + "rivermap_mainstreams.png", path + "rivermap_corrected.png")
mask_landsea(path + "rivermap_corrected.png", path + "landsea.png", path + "rivermap_masked.png")
check_image_for_more_than_two_blue(path + "rivermap_masked.png")
