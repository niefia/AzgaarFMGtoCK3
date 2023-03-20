import json
from PIL import Image, ImageDraw
import numpy as np
import sys

# set scaling factor
scaling_factor = 30

# print the scaling factor
print("Scaling factor: " + str(scaling_factor))

# Constants for blue, greeen and magenta
blue = (0, 0, 255)
green = (0, 255, 0)
magenta = (255,0,128)
white = (255, 255, 255)
red = (255, 0, 0)

# Declare a debug variable
debug = True


def paint_land_sea(heightmap_file, output_file):
    """Takes in a heightmap file, paints land white and sea magenta, outputs a PIL image object."""

    img = Image.open(heightmap_file)
    img = img.convert('RGB')

    # converting to numpy array for faster processing
    color_array = np.array(img)
    red, green, blue = color_array.T  # Temporarily unpack the bands for readability

    # Replace sea with magenta, land with white
    sea_pixels = ((red == 0) & (blue == 0) & (green == 0)).T
    color_array[sea_pixels] = magenta  # replacing sea pixels
    color_array[~sea_pixels] = white  # replacing "not-sea" pixels

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

    with open(rivers_geojson, "r") as riverData:
        data = json.load(riverData)

    # get rivers
    rivers = data["features"]

    print("Number of rivers: " + str(len(rivers)))
    for river in rivers:
        # We will process all rivers
        if river["properties"]:


            # For debug sp that we can eisier undertand what is going on
            # get river name
            river_name = river["properties"]["name"]
            #Get river type
            river_type = river["properties"]["type"]
            #Get river parent
            river_parent = river["properties"]["parent"]
            # Print the river name, type and parent ID to the console.
            print("Drawing mainstream: " + river_name + " of type " + river_type + " with parent ID " + str(river_parent))

            flat_coords = np.array([item * scaling_factor for sublist in river["geometry"]["coordinates"]
                                    for item in sublist])
            centred_coords = flat_coords + np.tile([img_width / 2, img_height / 2], int(flat_coords.size / 2))
            centred_coords = centred_coords.reshape(int(len(centred_coords) / 2), 2)  # reshaping into 2-column array

            draw_coords = np.floor(centred_coords[0]).reshape(1, 2)  # first coordinates to add


            # When drawing any river, monitor the number of magenta pixels that was detexted at river position.
            # If the river ends on a magenta, remove all but a few (mageenta_pixel_limit) pixels from the river, to avoid offshore river overlaps.

            magenta_pixel_count = 0
            mageenta_pixel_limit = 3


            # Find the pixel corrdinates of the river line
            for row in range(1, centred_coords[1:].shape[0]):
                new_coords = np.floor(centred_coords[row]).reshape(1, 2) #This is the 2d Array that holds the coordinates of the river line.
                # Print the river coordinates to the console if debug is true, and it is the first river in the list.
                if debug and river == rivers[0]:
                    print("River coordinates: " + str(new_coords) + " Existing pixel colour: " + str(img.getpixel((new_coords[0][0], new_coords[0][1]))))
                    #Also print the cuurrent image pixel colour to the console.



                #Try if the pixel at the cooridnate is magenta, then we increment the magenta pixel count
                try:
                    if img.getpixel((new_coords[0][0], new_coords[0][1])) == magenta:
                        magenta_pixel_count += 1
                    #If the pixel is not magenta, then we reset the magenta pixel count
                    else:
                        magenta_pixel_count = 0
                except:
                    print("Error: Pixel out of bounds")

                # TODO Better translation of coorinates to pixels
                
                if (np.abs(new_coords - draw_coords[-1]).sum(axis=1) >= 2)[0]:  # if both x and y coordinates jump
                    jump_coord = np.argmin(np.abs(draw_coords[-1] - centred_coords[row]))  # the closest of x or y
                    new_coords[0, jump_coord] = draw_coords[-1, jump_coord]
                    draw_coords = np.append(draw_coords, new_coords, axis=0)
                elif (np.abs(new_coords - draw_coords[-1]).sum(axis=1) == 1)[0]:  # at least one of x or y moves
                    draw_coords = np.append(draw_coords, new_coords, axis=0)

                # If the magenta pixel limit is not 0. We will remove the last few pixels from the river line equal to the magenta pixel limit.
                if mageenta_pixel_limit != 0:
                    if magenta_pixel_count >= mageenta_pixel_limit:
                        #Remove the last few pixels from the river line equal to the magenta pixel limit.
                        draw_coords = draw_coords[:-mageenta_pixel_limit]
                        #Set the magenta pixel count to 0
                        magenta_pixel_count = 0

            # We have the river coloured in, but not saved to the map, so now we need to do some error checking.
            # First we need to check that this river isn't going to be drawn over another river.
            # We do this by checking each pixel in the river line, and if it is already blue, we throw an error.

            # For each pixel in the river line, check the pixel in the image.
            #for pixel in draw_coords:
                #Get the pixel colour value
                #pixel_value = img.getpixel((pixel[0], pixel[1]))

                # If the pixel is blue, then we have a problem.
                #if img.getpixel((pixel[0], pixel[1])) == blue:
                    #Throw an error and specify where the error is.
                    #raise Exception("Error: River " + river_name + " is being drawn over another river at pixel " + str(pixel[0]) + ", " + str(pixel[1]) + ".")

            # start_color = green  # beginning color is green for source river
            # Draw the river river to the map
            try:
                draw.line(sum(draw_coords.tolist(), []), fill=blue)  # draw the river line
            except:
                print("Error: Pixel out of bounds")
            # draw.point(draw_coords[0].tolist(), fill=start_color)  # Recolours the starting point of the river
            # TODO: Error checking the area around the river to make sure all pixels are valid


    img = img.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(output_file, "PNG")
    #System open the image for debug purposes
    img.show()


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
                if pixels[x, y] == green:
                    # Count the adjacent blue pixels
                    count = 0
                    adj_blues = []
                    if x > 0 and pixels[x - 1, y] == blue:
                        count += 1
                        adj_blues.append((x - 1, y))
                    if x < image.size[0] - 1 and pixels[x + 1, y] == blue:
                        count += 1
                        adj_blues.append((x + 1, y))
                    if y > 0 and pixels[x, y - 1] == blue:
                        count += 1
                        adj_blues.append((x, y - 1))
                    if y < image.size[1] - 1 and pixels[x, y + 1] == blue:
                        count += 1
                        adj_blues.append((x, y + 1))
                    # Check if the green pixel has more than one adjacent blue pixel
                    if count > 1:
                        for bx, by in adj_blues:
                            # Check if the blue pixel has only one adjacent blue pixel
                            bcount = 0
                            if bx > 0 and pixels[bx - 1, by] == blue:
                                bcount += 1
                            if bx < image.size[0] - 1 and pixels[bx + 1, by] == blue:
                                bcount += 1
                            if by > 0 and pixels[bx, by - 1] == blue:
                                bcount += 1
                            if by < image.size[1] - 1 and pixels[bx, by + 1] == blue:
                                bcount += 1
                            if bcount == 0:
                                # Replace the blue pixel with white
                                new_pixels[bx, by] = white
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


# Use Landsea file as mask image as most Blue errors happen in sea, so can be masked anyway
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
        print(x, "/8192")
        for y in range(height):
            # Get the color of the pixel
            r, g, b = mask.getpixel((x, y))
            # If the color is magenta (FF0080), set the corresponding pixel in the original image to transparent
            if (r == 255) and (g == 0) and (b == 128):
                img.putpixel((x, y), (255, 0, 128, 0))

    # Save the modified image
    img.save(output_image_path)


# Checks for error of more than 2 touching Blue pixels, Does not correct yet
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
            if pixels[x, y] == blue:
                # Count the adjacent blue pixels
                count = 0
                if x > 0 and pixels[x - 1, y] == blue:
                    count += 1
                if x < image.size[0] - 1 and pixels[x + 1, y] == blue:
                    count += 1
                if y > 0 and pixels[x, y - 1] == blue:
                    count += 1
                if y < image.size[1] - 1 and pixels[x, y + 1] == blue:
                    count += 1
                # Check if the green pixel has more than one adjacent blue pixel
                if count > 2:
                    print("Error Blue pixel with more than 2 adjacent at ({}, {})".format(x, y), "Blue Pixel Error:",
                          (bpc))
                    bpc += 1


# Test Region of the code

# Path to folder containing heightmap.png, landsea.png, rivers.geojson when testing
path = "River_Test/"

paint_land_sea(path + "heightmap.png", path + "landsea.png")
draw_rivers(path + "landsea.png", path + "rivers.geojson", path + "rivermap_mainstreams.png")
#correct_rivermap(path + "rivermap_mainstreams.png", path + "rivermap_corrected.png")
#mask_landsea(path + "rivermap_corrected.png", path + "landsea.png", path + "rivermap_masked.png")
#check_image_for_more_than_two_blue(path + "rivermap_masked.png")
